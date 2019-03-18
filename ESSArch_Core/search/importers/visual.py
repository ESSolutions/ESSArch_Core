# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import uuid

import pytz
from countries_plus.models import Country
from django.core.cache import cache
from django.db import transaction
from django.utils import dateparse, timezone
from languages_plus.models import Language
from lxml import etree

from ESSArch_Core.agents.models import (
    Agent,
    AgentIdentifier,
    AgentIdentifierType,
    AgentName,
    AgentNameType,
    AgentNote,
    AgentNoteType,
    AgentPlace,
    AgentPlaceType,
    AgentTagLink,
    AgentTagLinkRelationType,
    AgentType,
    MainAgentType,
    RefCode,
    Topography,
)
from ESSArch_Core.search.importers.base import BaseImporter
from ESSArch_Core.agents.documents import AgentDocument
from ESSArch_Core.tags.documents import Archive, Component, StructureUnitDocument
from ESSArch_Core.tags.models import (
    Structure,
    StructureUnit,
    Tag,
    TagStructure,
    TagVersion,
)

logger = logging.getLogger('essarch.search.importers.VisualImporter')


class VisualImporter(BaseImporter):
    NSMAP = {'va': 'http://www.visualarkiv.se/vaxml/v6.1'}

    ARKIV_XPATH = etree.XPath("va:arkiv", namespaces=NSMAP)
    SERIE_XPATH = etree.XPath("va:serier/va:serie", namespaces=NSMAP)
    VOLYM_XPATH = etree.XPath("va:volymer/va:volym", namespaces=NSMAP)

    AGENT_IDENTIFIER_TYPE = 'Visual arkivbildarnummer'
    AGENT_NAME_TYPE = 'auktoriserad'
    COUNTRY_CODE = 'SE'
    REPO_CODE = 'SVK'  # TODO: just a dummy

    AGENT_TAG_LINK_RELATION_TYPE, _ = AgentTagLinkRelationType.objects.get_or_create(name='creator')

    REF_CODE, _ = RefCode.objects.get_or_create(
        country=Country.objects.get(iso=COUNTRY_CODE),
        repository_code=REPO_CODE,
    )
    LANGUAGE = Language.objects.get(iso_639_1='sv')

    @classmethod
    def parse_agent_type(cls, arkivbildare):
        main_agent_type, _ = MainAgentType.objects.get_or_create(
            name=arkivbildare.xpath("va:verksamtyp/va:typkod", namespaces=cls.NSMAP)[0].text,
        )
        agent_type, _ = AgentType.objects.get_or_create(
            cpf=arkivbildare.get('ipstyp'),
            main_type=main_agent_type,
        )

        return agent_type

    @classmethod
    def parse_agent_names(cls, arkivbildare, agent):
        agent_name_type, _ = AgentNameType.objects.get_or_create(name=cls.AGENT_NAME_TYPE)

        name = AgentName.objects.create(
            agent=agent,
            main=arkivbildare.xpath("va:arkivbildarnamn", namespaces=cls.NSMAP)[0].text,
            type=agent_name_type,
        )
        return [name]

    @classmethod
    def parse_agent_notes(cls, arkivbildare, agent):
        notes = []

        tidnamn = arkivbildare.xpath("va:tidnamn", namespaces=cls.NSMAP)[0]
        if tidnamn.text:
            note_type_admin_anmerkning, _ = AgentNoteType.objects.get_or_create(
                name='administrativ anmärkning'
            )
            note = AgentNote.objects.create(
                agent=agent,
                type=note_type_admin_anmerkning,
                text=tidnamn.text,
                create_date=timezone.now(),  # TODO: change model to allow null?
            )
            notes.append(note)

        historik = arkivbildare.xpath("va:historik", namespaces=cls.NSMAP)
        if len(historik) and historik[0].text:
            historik = historik[0]
            historik_text = ''.join(historik.itertext()).replace('\n', '<br />')

            note_type_historik, _ = AgentNoteType.objects.get_or_create(
                name='historik',
            )
            note = AgentNote.objects.create(
                agent=agent,
                type=note_type_historik,
                text=historik_text,
                create_date=timezone.now(),  # TODO: change model to allow null?
                revise_date=dateparse.parse_datetime(historik.get('andraddat'))
            )
            notes.append(note)

        return notes

    @classmethod
    def parse_agent_identifiers(cls, arkivbildare, agent):
        identifier_type, _ = AgentIdentifierType.objects.get_or_create(name=cls.AGENT_IDENTIFIER_TYPE)

        identifier = AgentIdentifier.objects.create(
            agent=agent,
            identifier=arkivbildare.get('arkivbildarnr'),
            type=identifier_type,
        )
        return [identifier]

    @classmethod
    def parse_agent_places(cls, arkivbildare, agent):
        ort = arkivbildare.xpath("va:ort", namespaces=cls.NSMAP)[0].text
        if ort:
            topography, _ = Topography.objects.get_or_create(
                name=ort,
                type='Egen',
            )
            agent_place_type, _ = AgentPlaceType.objects.get_or_create(
                name='verksamhetsort'
            )
            AgentPlace.objects.create(
                agent=agent,
                topography=topography,
                type=agent_place_type,
            )

    @classmethod
    def parse_agent_start_date(cls, arkivbildare):
        start_year = arkivbildare.xpath('va:verksamf', namespaces=cls.NSMAP)[0].text
        start_date = None
        if start_year:
            start_date = datetime(
                year=int(start_year), month=1, day=1,
                tzinfo=pytz.UTC,
            )

        return start_date

    @classmethod
    def parse_agent_end_date(cls, arkivbildare):
        end_year = arkivbildare.xpath('va:verksamt', namespaces=cls.NSMAP)[0].text
        end_date = None
        if end_year:
            end_date = datetime(
                year=int(end_year), month=1, day=1,
                tzinfo=pytz.UTC,
            )

        return end_date

    @classmethod
    def parse_arkivbildare(cls, el, task=None):
        logger.info("Parsing arkivbildare...")

        agent_type = cls.parse_agent_type(el)
        start_date = cls.parse_agent_start_date(el)
        end_date = cls.parse_agent_end_date(el)

        agent = Agent.objects.create(
            type=agent_type,
            ref_code=cls.REF_CODE,
            level_of_detail=Agent.PARTIAL,
            record_status=Agent.DRAFT,
            script=Agent.LATIN,
            language=cls.LANGUAGE,
            create_date=timezone.now(),  # TODO: change model to allow null?
            start_date=start_date,
            end_date=end_date,
            task=task,
        )

        cls.parse_agent_names(el, agent)
        cls.parse_agent_notes(el, agent)
        cls.parse_agent_identifiers(el, agent)
        cls.parse_agent_places(el, agent)

        doc = AgentDocument.from_obj(agent)

        logger.info("Parsed arkivbildare: {}".format(agent.pk))

        return agent, doc.to_dict(include_meta=True)

    @classmethod
    def save_tags(cls, tags, tag_versions, tag_structures, tag_links):
        logger.info("Saving tags...")

        Tag.objects.bulk_create(tags, batch_size=100)
        TagVersion.objects.bulk_create(tag_versions, batch_size=100)
        with transaction.atomic():
            with TagStructure.objects.disable_mptt_updates():
                TagStructure.objects.bulk_create(tag_structures, batch_size=100)

        AgentTagLink.objects.bulk_create(tag_links, batch_size=100)

        logger.info("Tags saved")

    @classmethod
    def parse_serier(cls, arkiv_el, agent, arkiv_version, arkiv_structure, task, ip):
        volym_tags = []
        volym_versions = []
        volym_structures = []
        volym_links = []

        with StructureUnit.objects.delay_mptt_updates():
            logger.info('Parsing series of {}...'.format(arkiv_version.pk))
            for serie_el in cls.get_serier(arkiv_el):
                structure_unit = cls.parse_serie(
                    serie_el, arkiv_structure.structure, agent=agent, task=task, ip=ip,
                )

                logger.info('Parsing volumes of structure unit {}'.format(structure_unit.reference_code))
                for volym_el in cls.get_volymer(serie_el):
                    doc, volym_tag, volym_version, volym_structure, volym_link = cls.parse_volym(
                        volym_el, arkiv_version, arkiv_structure, structure_unit, agent, task=task, ip=ip
                    )
                    yield doc

                    volym_tags.append(volym_tag)
                    volym_versions.append(volym_version)
                    volym_structures.append(volym_structure)
                    volym_links.append(volym_link)

                logger.info('Volumes of structure unit {} successfully parsed'.format(structure_unit.reference_code))

            logger.info('Series of {} successfully parsed'.format(arkiv_version.pk))

        cls.save_tags(volym_tags, volym_versions, volym_structures, volym_links)

    @classmethod
    def create_arkiv(cls, arkivbildare, agent, task=None, ip=None):
        for arkiv_el in cls.get_arkiv(arkivbildare):
            doc, arkiv_tag, arkiv_version, arkiv_structure, arkiv_link = cls.parse_arkiv(
                arkiv_el, agent, task=task, ip=ip
            )

            yield doc
            yield from cls.parse_serier(arkiv_el, agent, arkiv_version, arkiv_structure, task, ip)

    @staticmethod
    def get_arkiv(arkivbildare):
        return VisualImporter.ARKIV_XPATH(arkivbildare)

    @staticmethod
    def get_serier(arkiv):
        return VisualImporter.SERIE_XPATH(arkiv)

    @staticmethod
    def get_volymer(serie):
        return VisualImporter.VOLYM_XPATH(serie)

    @classmethod
    def parse_arkiv(cls, el, agent, task=None, ip=None):
        logger.info("Parsing arkiv...")
        name = el.xpath("va:arkivnamn", namespaces=cls.NSMAP)[0].text
        tag_type = 'Arkiv'

        start_year = el.xpath("va:tidarkivf", namespaces=cls.NSMAP)[0].text
        start_date = None
        if start_year is not None:
            start_date = datetime(
                year=int(start_year), month=1, day=1,
                tzinfo=pytz.UTC,
            )

        end_year = el.xpath("va:tidarkivt", namespaces=cls.NSMAP)[0].text
        end_date = None
        if end_year is not None:
            end_date = datetime(
                year=int(end_year), month=1, day=1,
                tzinfo=pytz.UTC,
            )

        tag = Tag.objects.create(information_package=ip, task=task)
        tag_version = TagVersion.objects.create(
            tag=tag,
            elastic_index='archive',
            type=tag_type,
            name=name,
            start_date=start_date,
            end_date=end_date,
        )

        structure = Structure.objects.create(
            name="Arkivförteckning för {}".format(name),
            version='1.0',
        )

        tag_structure = TagStructure.objects.create(
            tag=tag,
            structure=structure,
        )

        agent_tag_link = AgentTagLink.objects.create(
            agent=agent,
            tag_id=tag_version.id,
            type=cls.AGENT_TAG_LINK_RELATION_TYPE,
        )

        doc = Archive.from_obj(tag_version)
        doc.agents = [str(agent.pk)]

        logger.info("Parsed arkiv: {}".format(tag_version.pk))
        return doc.to_dict(include_meta=True), tag, tag_version, tag_structure, agent_tag_link

    @classmethod
    def parse_serie(cls, el, structure, agent=None, task=None, ip=None):
        logger.debug("Parsing serie...")
        name = el.xpath("va:serierubrik", namespaces=cls.NSMAP)[0].text
        tag_type = el.get('level')
        reference_code = el.get("signum")

        parent_unit_id = None
        parent_reference_code = reference_code

        cache_key_prefix = str(structure.pk)

        while len(parent_reference_code) > 1:
            parent_reference_code = parent_reference_code.rsplit(maxsplit=1)[0]
            cache_key = '{}{}'.format(cache_key_prefix, parent_reference_code)
            parent_unit_id = cache.get(cache_key)

            if parent_unit_id is not None:
                break

        unit = StructureUnit.objects.create(
            structure=structure,
            name=name,
            parent_id=parent_unit_id,
            type=tag_type,
            reference_code=reference_code,
            task=task,
        )
        doc = StructureUnitDocument.from_obj(unit)
        doc.save()

        cache.set('{}{}'.format(cache_key_prefix, reference_code), str(unit.pk), 300)

        # TODO: store in new index in elasticsearch?

        logger.debug("Parsed serie: {}".format(unit.pk))
        return unit

    @classmethod
    def parse_volym(cls, el, archive_version, parent_tag_structure, structure_unit, agent, task=None, ip=None):
        logger.debug("Parsing volym...")
        ref_code = el.xpath("va:volnr", namespaces=cls.NSMAP)[0].text
        name = el.xpath("va:utseende", namespaces=cls.NSMAP)[0].text
        tag_type = "Volym"

        volym_id = uuid.uuid4()

        tag = Tag(information_package=ip, task=task)
        tag_version = TagVersion(
            pk=volym_id,
            tag=tag,
            elastic_index='component',
            reference_code=ref_code,
            name=name,
            type=tag_type,
        )
        tag_structure = TagStructure(
            tag=tag,
            structure_unit=structure_unit,
            structure=parent_tag_structure.structure,
            parent=parent_tag_structure,
            tree_id=parent_tag_structure.tree_id,
            lft=0,
            rght=0,
            level=0
        )

        agent_tag_link = AgentTagLink(
            agent=agent,
            tag_id=tag_version.id,
            type=cls.AGENT_TAG_LINK_RELATION_TYPE,
        )

        doc = Component.from_obj(tag_version, archive=str(archive_version.pk))
        doc.agents = [str(agent.pk)]

        logger.debug("Parsed volym: {}".format(tag_version.pk))
        return doc.to_dict(include_meta=True), tag, tag_version, tag_structure, agent_tag_link

    def import_content(self, path, rootdir=None, ip=None, **extra_paths):
        self.indexed_files = []
        self.ip = ip

        logger.info("Importing data from {}...".format(path))
        self.cleanup()
        self.parse_xml(path)
        logger.info("Data imported from {}".format(path))

    def cleanup(self):
        logger.info("Deleting task agents already in database...")
        Agent.objects.filter(task=self.task).delete()
        logger.info("Deleted task agents already in database")

        # TODO: Delete Structures connected to task?
        logger.info("Deleting task structure units already in database...")
        StructureUnit.objects.filter(task=self.task).delete()
        logger.info("Deleted task structure units already in database")

        logger.info("Deleting task tags already in database...")
        Tag.objects.filter(task=self.task).delete()
        logger.info("Deleted task tags already in database")

        self.cleanup_elasticsearch(self.task)

    @transaction.atomic
    def parse_xml(self, xmlfile):
        logger.info("Parsing XML elements...")

        tree = etree.parse(xmlfile, self.xmlparser)
        root = tree.getroot()

        all_docs = []

        with TagStructure.objects.disable_mptt_updates():
            for arkivbildare in root.xpath("va:arkivbildare", namespaces=self.NSMAP):
                agent, doc = self.parse_arkivbildare(arkivbildare, task=self.task)
                all_docs.append(doc)

                docs = list(self.create_arkiv(arkivbildare, agent, task=self.task, ip=self.ip))
                all_docs.extend(docs)

        logger.info("XML elements parsed")

        self.update_current_tag_versions()

        total = None
        if self.task is not None:
            total = TagVersion.objects.filter(tag__task=self.task).count()

        for _, count in self.save_to_elasticsearch(all_docs):
            if self.task is not None:
                partial_progress = ((count / total) / 4) * 100
                self.task.update_progress(75 + partial_progress)

        logger.info("Rebuilding trees...")
        TagStructure.objects.rebuild()
        logger.info("Trees rebuilt")