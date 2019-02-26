# -*- coding: utf-8 -*-

from datetime import datetime
import logging

import pytz
from countries_plus.models import Country
from django.db import transaction
from django.utils import timezone
from languages_plus.models import Language
from lxml import etree

from ESSArch_Core.search.importers.base import BaseImporter
from ESSArch_Core.tags.models import (
    Agent,
    AgentIdentifier,
    AgentIdentifierType,
    AgentName,
    AgentNameType,
    AgentNote,
    AgentNoteType,
    AgentPlace,
    AgentPlaceType,
    AgentType,
    MainAgentType,
    RefCode,
    Topography,
)

logger = logging.getLogger('essarch.search.importers.KlaraImporter')


class KlaraImporter(BaseImporter):
    AGENT_IDENTIFIER_TYPE = 'Klara'
    AGENT_NAME_TYPE = 'auktoriserad'
    AGENT_ALT_NAME_TYPE = 'alternativt'
    COUNTRY_CODE = 'SE'
    LANGUAGE_CODE = 'sv'
    REPO_CODE = 'C020'  # TODO: just a dummy

    _ref_code = None
    _language = None
    _name_type = None
    _alt_name_type = None
    _note_type_anmarkning = None
    _note_type_historik = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def ref_code(self):
        if self._ref_code is None:
            self._ref_code, _ = RefCode.objects.get_or_create(
                country=Country.objects.get(iso=self.COUNTRY_CODE),
                repository_code=self.REPO_CODE,
            )
        return self._ref_code

    @property
    def language(self):
        if self._language is None:
            self._language = Language.objects.get(iso_639_1=self.LANGUAGE_CODE)
        return self._language

    @property
    def name_type(self):
        if self._name_type is None:
            self._name_type, _ = AgentNameType.objects.get_or_create(name=self.AGENT_NAME_TYPE)
        return self._name_type

    @property
    def alt_name_type(self):
        if self._alt_name_type is None:
            self._alt_name_type, _ = AgentNameType.objects.get_or_create(name=self.AGENT_ALT_NAME_TYPE)
        return self._alt_name_type

    @property
    def note_type_anmarkning(self):
        if self._note_type_anmarkning is None:
            self._note_type_anmarkning, _ = AgentNoteType.objects.get_or_create(name='administrativ anmärkning')
        return self._note_type_anmarkning

    @property
    def note_type_historik(self):
        if self._note_type_historik is None:
            self._note_type_historik, _ = AgentNoteType.objects.get_or_create(name='historik')
        return self._note_type_historik

    @staticmethod
    def _parse_timestamp(ts):
        date_format = "%Y-%m-%d %H:%M:%S:%f"
        tPart, tzPart = ts.rsplit(' ', 1)
        tzPart = tzPart.replace('CEST', 'CET')

        dt = datetime.strptime(tPart, date_format)
        tz = pytz.timezone(tzPart)
        return tz.localize(dt)

    @classmethod
    def parse_agent_type(cls, arkivbildare):
        main_agent_type, _ = MainAgentType.objects.get_or_create(
            name=arkivbildare.xpath("ObjectParts/General/ArchiveOrig.Parent.Name")[0].text,
        )

        category_name = arkivbildare.xpath("ObjectParts/General/ArchOrigCategory.Name")[0].text
        if category_name == 'Person (släkt)':
            cpf = AgentType.PERSON
        else:
            cpf = AgentType.CORPORATE_BODY

        agent_type, _ = AgentType.objects.get_or_create(
            cpf=cpf,
            main_type=main_agent_type,
            sub_type=category_name,
        )

        return agent_type

    @classmethod
    def _parse_agent_alternative_names(cls, arkivbildare, agent, name_type):
        for name_el in arkivbildare.xpath("ObjectParts/AltNames/ArchiveOrig.AltNames/ArchOrigAltName"):
            alt_name = AgentName.objects.create(
                agent=agent,
                main=name_el.xpath("ArchOrigAltName.Name")[0].text,
                type=name_type,
                start_date=datetime.strptime(name_el.xpath("ArchOrigAltName.UsedFrom")[0].text, '%Y'),
                end_date=datetime.strptime(name_el.xpath("ArchOrigAltName.UsedTo")[0].text, '%Y'),
            )
            yield alt_name

    @classmethod
    def parse_agent_names(cls, arkivbildare, agent, name_type, alt_name_type):
        authorized_name = AgentName.objects.create(
            agent=agent,
            main=arkivbildare.xpath("ObjectParts/General/ArchiveOrig.Name")[0].text,
            type=name_type,
        )

        alt_names = list(cls._parse_agent_alternative_names(arkivbildare, agent, alt_name_type))
        return [authorized_name] + alt_names

    @classmethod
    def parse_agent_notes(cls, arkivbildare, agent, anmarkning_type, historik_type):
        notes = []

        create_date = cls.parse_agent_create_date(arkivbildare)
        created_by = cls.parse_agent_created_by(arkivbildare)

        created_text = (
            'Auktoritetsposten upprättades {date} i arkivredovisningssystemet Klara av användare {name}'.format(
                date=create_date,
                name=created_by,
            )
        )
        created_note = AgentNote.objects.create(
            agent=agent,
            type=anmarkning_type,
            text=created_text,
            create_date=timezone.now(),
        )
        notes.append(created_note)

        revise_date = cls.parse_agent_revise_date(arkivbildare)
        revised_by = cls.parse_agent_revised_by(arkivbildare)

        revised_text = (
            'Auktoritetsposten ändrades {date} i arkivredovisningssystemet Klara av användare {name}'.format(
                date=revise_date,
                name=revised_by,
            )
        )
        revised_note = AgentNote.objects.create(
            agent=agent,
            type=anmarkning_type,
            text=revised_text,
            create_date=timezone.now(),
        )
        notes.append(revised_note)

        historik = arkivbildare.xpath("ObjectParts/Notes/ArchiveOrig.Notes")
        if len(historik) and historik[0].text:
            historik = historik[0].text

            note = AgentNote.objects.create(
                agent=agent,
                type=historik_type,
                text=historik,
                create_date=cls.parse_agent_revise_date(arkivbildare),
                revise_date=cls.parse_agent_revise_date(arkivbildare),
            )
            notes.append(note)

        return notes

    @classmethod
    def parse_agent_identifiers(cls, arkivbildare, agent):
        identifier_type, _ = AgentIdentifierType.objects.get_or_create(name=cls.AGENT_IDENTIFIER_TYPE)
        identifier_text = arkivbildare.xpath("ObjectKey/ArchiveOrig.ArchiveOrigID")[0].text

        identifier = AgentIdentifier.objects.create(
            agent=agent,
            identifier='{}/{}'.format(cls.REPO_CODE, identifier_text),
            type=identifier_type,
        )
        return [identifier]

    @classmethod
    def parse_agent_topography(cls, arkivbildare):
        name = arkivbildare.xpath("ObjectParts/General/ArchiveOrig.TopographicName")[0].text

        if name is None:
            return None

        topography, _ = Topography.objects.get_or_create(
            name=name,
            type='Lokal term',
        )
        return topography

    @classmethod
    def parse_agent_places(cls, arkivbildare, agent):
        topography = cls.parse_agent_topography(arkivbildare)
        agent_place_type, _ = AgentPlaceType.objects.get_or_create(
            name='verksamhetsort'
        )
        AgentPlace.objects.create(
            agent=agent,
            topography=topography,
            type=agent_place_type,
        )

    @classmethod
    def parse_agent_level_of_detail(cls, arkivbildare):
        publish = arkivbildare.xpath('ObjectParts/General/ArchiveOrig.Publish')[0].text
        if publish == 'true':
            return Agent.FULL

        return Agent.PARTIAL

    @classmethod
    def parse_agent_record_status(cls, arkivbildare):
        publish = arkivbildare.xpath('ObjectParts/General/ArchiveOrig.Publish')[0].text
        if publish == 'true':
            return Agent.FINAL

        return Agent.DRAFT

    @classmethod
    def parse_agent_create_date(cls, arkivbildare):
        try:
            date_string = arkivbildare.xpath('ObjectParts/General/ArchiveOrig.CreatedWhen')[0].text
            if date_string is None:
                return cls.parse_agent_revise_date(arkivbildare)

            return cls._parse_timestamp(date_string)
        except IndexError:
            return cls.parse_agent_revise_date(arkivbildare)

    @classmethod
    def parse_agent_created_by(cls, arkivbildare):
        return arkivbildare.xpath('ObjectParts/General/ArchiveOrig.CreatedBy')[0].text

    @classmethod
    def parse_agent_revise_date(cls, arkivbildare):
        date_string = arkivbildare.xpath('ObjectParts/General/ArchiveOrig.ModifiedWhen')[0].text
        return cls._parse_timestamp(date_string)

    @classmethod
    def parse_agent_revised_by(cls, arkivbildare):
        return arkivbildare.xpath('ObjectParts/General/ArchiveOrig.ModifiedBy')[0].text

    @classmethod
    def parse_agent_start_date(cls, arkivbildare):
        start_year = arkivbildare.xpath('ObjectParts/General/ArchiveOrig.ExistFrom')[0].text
        start_date = None
        if start_year:
            start_date = datetime.strptime(start_year, '%Y')

        return start_date

    @classmethod
    def parse_agent_end_date(cls, arkivbildare):
        end_year = arkivbildare.xpath('ObjectParts/General/ArchiveOrig.ExistTo')[0].text
        end_date = None
        if end_year:
            end_date = datetime.strptime(end_year, '%Y')

        return end_date

    def parse_arkivbildare(self, el, task=None):
        logger.debug("Parsing arkivbildare...")

        agent_type = self.parse_agent_type(el)

        level_of_detail = self.parse_agent_level_of_detail(el)
        record_status = self.parse_agent_record_status(el)

        create_date = self.parse_agent_create_date(el)
        revise_date = self.parse_agent_revise_date(el)

        start_date = self.parse_agent_start_date(el)
        end_date = self.parse_agent_end_date(el)

        agent = Agent.objects.create(
            type=agent_type,
            ref_code=self.ref_code,
            level_of_detail=level_of_detail,
            record_status=record_status,
            script=Agent.LATIN,
            language=self.language,
            create_date=create_date,
            revise_date=revise_date,
            start_date=start_date,
            end_date=end_date,
            task=task,
        )

        self.parse_agent_names(el, agent, self.name_type, self.alt_name_type)
        self.parse_agent_notes(el, agent, self.note_type_anmarkning, self.note_type_historik)
        self.parse_agent_identifiers(el, agent)
        self.parse_agent_places(el, agent)

        logger.info("Parsed arkivbildare: {}".format(agent.pk))

        return agent

    def import_content(self, path, rootdir=None, ip=None):
        self.indexed_files = []
        self.ip = ip

        logger.debug("Importing data from {}...".format(path))
        self.cleanup()
        self.parse_xml(path)
        logger.info("Data imported from {}".format(path))

    def cleanup(self):
        logger.debug("Deleting task agents already in database...")
        Agent.objects.filter(task=self.task).delete()
        logger.info("Deleted task agents already in database")

    @transaction.atomic
    def parse_xml(self, xmlfile):
        logger.debug("Parsing XML elements...")

        tree = etree.parse(xmlfile, self.xmlparser)
        root = tree.getroot()

        for arkivbildare in root.xpath("ArchiveOrig"):
            self.parse_arkivbildare(arkivbildare, task=self.task)

        logger.info("XML elements parsed")