from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ESSArch_Core.tags.models import (
    NodeRelationType,
    Structure,
    StructureType,
    StructureUnit,
    StructureUnitRelation,
    StructureUnitType,
)
from ESSArch_Core.tags.serializers import PUBLISHED_STRUCTURE_CHANGE_ERROR

User = get_user_model()


class ListStructureTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('structure-list')
        self.user = User.objects.create(username='user')
        self.client.force_authenticate(user=self.user)

        self.structure_type = StructureType.objects.create(name='test')

    def create_structure(self):
        return Structure.objects.create(type=self.structure_type, is_template=True)

    def test_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_one_structure(self):
        self.create_structure()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_multiple_agents(self):
        self.create_structure()
        self.create_structure()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class CreateStructureTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('structure-list')

        self.user = User.objects.create(username='user')
        self.member = self.user.essauth_member

        self.client.force_authenticate(user=self.user)

    def test_without_permission(self):
        response = self.client.post(self.url,)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create(self):
        perm = Permission.objects.get(codename='add_structure')
        self.user.user_permissions.add(perm)
        self.client.force_authenticate(user=self.user)

        structure_type = StructureType.objects.create(name='test')

        response = self.client.post(
            self.url,
            data={
                'name': 'foo',
                'type': structure_type.pk,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Structure.objects.count(), 1)
        self.assertTrue(Structure.objects.filter(name='foo', created_by=self.user, revised_by=self.user).exists())


class UpdateStructureTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(username='user')
        self.member = self.user.essauth_member

        self.client.force_authenticate(user=self.user)

        self.structure_type = StructureType.objects.create(name='test')

    def create_structure(self):
        return Structure.objects.create(type=self.structure_type, is_template=True)

    def test_without_permission(self):
        structure = self.create_structure()
        url = reverse('structure-detail', args=[structure.pk])

        response = self.client.patch(
            url,
            data={
                'name': 'bar',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update(self):
        structure = self.create_structure()
        url = reverse('structure-detail', args=[structure.pk])

        perm = Permission.objects.get(codename='change_structure')
        self.user.user_permissions.add(perm)
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            url,
            data={
                'name': 'bar',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Structure.objects.count(), 1)
        self.assertTrue(Structure.objects.filter(name='bar', created_by=None, revised_by=self.user).exists())

    def test_update_published_structure(self):
        structure = self.create_structure()
        structure.published = True
        structure.save()
        url = reverse('structure-detail', args=[structure.pk])

        perm = Permission.objects.get(codename='change_structure')
        self.user.user_permissions.add(perm)
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            url,
            data={
                'name': 'bar',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'non_field_errors': [PUBLISHED_STRUCTURE_CHANGE_ERROR]})


class CreateStructureUnitTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(username='user')
        self.member = self.user.essauth_member

        perm = Permission.objects.get(codename='add_structureunit')
        self.user.user_permissions.add(perm)

        self.client.force_authenticate(user=self.user)

        self.structure_type = StructureType.objects.create(name='test')

    def create_structure(self):
        return Structure.objects.create(type=self.structure_type, is_template=True)

    def test_invalid_type(self):
        structure = self.create_structure()
        other_structure_type = StructureType.objects.create(name='other')
        unit_type = StructureUnitType.objects.create(name="test", structure_type=other_structure_type)

        url = reverse('structure-units-list', args=[structure.pk])

        response = self.client.post(
            url,
            data={
                'name': 'foo',
                'type': unit_type.pk,
                'reference_code': '123',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(StructureUnit.objects.exists())

    def test_valid_type(self):
        structure = self.create_structure()
        unit_type = StructureUnitType.objects.create(name="test", structure_type=structure.type)

        url = reverse('structure-units-list', args=[structure.pk])

        response = self.client.post(
            url,
            data={
                'name': 'foo',
                'type': unit_type.pk,
                'reference_code': '123',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StructureUnit.objects.count(), 1)
        self.assertTrue(StructureUnit.objects.filter(structure=structure).exists())

    def test_with_related_unit(self):
        structure = self.create_structure()
        unit_type = StructureUnitType.objects.create(name="test", structure_type=structure.type)
        other_unit = StructureUnit.objects.create(name="foo", reference_code="123", type=unit_type, structure=structure)

        relation_type = NodeRelationType.objects.create(name="test")
        url = reverse('structure-units-list', args=[structure.pk])

        response = self.client.post(
            url,
            data={
                'name': 'bar',
                'type': unit_type.pk,
                'reference_code': '456',
                'related_structure_units': [
                    {
                        'structure_unit': other_unit.pk,
                        'type': relation_type.pk,
                    }
                ],
            }
        )

        unit = StructureUnit.objects.get(name='bar')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StructureUnit.objects.count(), 2)
        self.assertEqual(StructureUnitRelation.objects.count(), 2)

        self.assertTrue(
            StructureUnitRelation.objects.filter(
                structure_unit_a=unit, structure_unit_b=other_unit, type=relation_type
            ).exists()
        )
        self.assertTrue(
            StructureUnitRelation.objects.filter(
                structure_unit_a=other_unit, structure_unit_b=unit, type=relation_type
            ).exists()
        )

    def test_with_related_unit_and_mirrored_type(self):
        structure = self.create_structure()
        unit_type = StructureUnitType.objects.create(name="test", structure_type=structure.type)
        other_unit = StructureUnit.objects.create(name="foo", reference_code="123", type=unit_type, structure=structure)

        relation_type = NodeRelationType.objects.create(name="test")
        mirrored_relation_type = NodeRelationType.objects.create(name="test_mirrored")
        relation_type.mirrored_type = mirrored_relation_type
        relation_type.save()

        url = reverse('structure-units-list', args=[structure.pk])

        response = self.client.post(
            url,
            data={
                'name': 'bar',
                'type': unit_type.pk,
                'reference_code': '456',
                'related_structure_units': [
                    {
                        'structure_unit': other_unit.pk,
                        'type': relation_type.pk,
                    }
                ],
            }
        )

        unit = StructureUnit.objects.get(name='bar')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StructureUnit.objects.count(), 2)
        self.assertEqual(StructureUnitRelation.objects.count(), 2)

        self.assertTrue(
            StructureUnitRelation.objects.filter(
                structure_unit_a=unit, structure_unit_b=other_unit, type=relation_type
            ).exists()
        )
        self.assertTrue(
            StructureUnitRelation.objects.filter(
                structure_unit_a=other_unit, structure_unit_b=unit, type=mirrored_relation_type
            ).exists()
        )


    def test_in_published_structure(self):
        structure = self.create_structure()
        structure.published = True
        structure.save()
        unit_type = StructureUnitType.objects.create(name="test", structure_type=structure.type)

        url = reverse('structure-units-list', args=[structure.pk])

        response = self.client.post(
            url,
            data={
                'name': 'foo',
                'type': unit_type.pk,
                'reference_code': '123',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'non_field_errors': [PUBLISHED_STRUCTURE_CHANGE_ERROR]})

    def test_in_structure_template_instance(self):
        template = self.create_structure()
        template.published = True
        template.save()

        instance = self.create_structure()
        instance.is_template = False
        instance.published = True
        instance.template = template
        instance.save()

        unit_type = StructureUnitType.objects.create(name="test", structure_type=instance.type)
        url = reverse('structure-units-list', args=[instance.pk])

        response = self.client.post(
            url,
            data={
                'name': 'foo',
                'type': unit_type.pk,
                'reference_code': '123',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UpdateStructureUnitTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(username='user')
        self.member = self.user.essauth_member

        perm = Permission.objects.get(codename='change_structureunit')
        self.user.user_permissions.add(perm)
        self.client.force_authenticate(user=self.user)

        self.structure_type = StructureType.objects.create(name='test')
        self.structure_unit_type = StructureUnitType.objects.create(name='test', structure_type=self.structure_type)

    def create_structure(self):
        return Structure.objects.create(type=self.structure_type, is_template=True)

    def create_structure_unit(self, structure, ref_code):
        return StructureUnit.objects.create(
            structure=structure,
            type=self.structure_unit_type,
            reference_code=ref_code
        )

    def test_update(self):
        structure = self.create_structure()
        structure_unit = self.create_structure_unit(structure, "1")
        url = reverse('structure-units-detail', args=[structure.pk, structure_unit.pk])

        response = self.client.patch(
            url,
            data={
                'name': 'bar',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(StructureUnit.objects.count(), 1)
        self.assertTrue(StructureUnit.objects.filter(name='bar').exists())

    def test_update_published_structure(self):
        structure = self.create_structure()
        structure.published = True
        structure.save()

        structure_unit = self.create_structure_unit(structure, "1")
        url = reverse('structure-units-detail', args=[structure.pk, structure_unit.pk])

        response = self.client.patch(
            url,
            data={
                'name': 'bar',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'non_field_errors': [PUBLISHED_STRUCTURE_CHANGE_ERROR]})

        # relations can be changed even on published structures
        other_structure_unit = self.create_structure_unit(structure, "2")
        relation_type = NodeRelationType.objects.create(name="test")
        response = self.client.patch(
            url,
            data={
                'related_structure_units': [
                    {
                        'structure_unit': other_structure_unit.pk,
                        'type': relation_type.pk,
                    }
                ],
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # but not together with other data
        response = self.client.patch(
            url,
            data={
                'name': 'bar',
                'related_structure_units': [
                    {
                        'structure_unit': other_structure_unit.pk,
                        'type': relation_type.pk,
                    }
                ],
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'non_field_errors': [PUBLISHED_STRUCTURE_CHANGE_ERROR]})
