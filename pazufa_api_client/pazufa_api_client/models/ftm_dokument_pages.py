from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.mime import Mime
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.ftm_dokument_pages_address_entity import FtmDokumentPagesAddressEntity
  from ..models.ftm_dokument_pages_ancestors_item import FtmDokumentPagesAncestorsItem
  from ..models.ftm_dokument_pages_candidate_similars_item import FtmDokumentPagesCandidateSimilarsItem
  from ..models.ftm_dokument_pages_court_case_item import FtmDokumentPagesCourtCaseItem
  from ..models.ftm_dokument_pages_documented_by import FtmDokumentPagesDocumentedBy
  from ..models.ftm_dokument_pages_match_similars_item import FtmDokumentPagesMatchSimilarsItem
  from ..models.ftm_dokument_pages_mentioned_entities_item import FtmDokumentPagesMentionedEntitiesItem
  from ..models.ftm_dokument_pages_note_entities import FtmDokumentPagesNoteEntities
  from ..models.ftm_dokument_pages_proof import FtmDokumentPagesProof
  from ..models.ftm_dokument_pages_proven_intervals_item import FtmDokumentPagesProvenIntervalsItem
  from ..models.ftm_dokument_pages_proven_item import FtmDokumentPagesProvenItem
  from ..models.ftm_dokument_pages_related_entities_item import FtmDokumentPagesRelatedEntitiesItem
  from ..models.ftm_dokument_pages_risks_item import FtmDokumentPagesRisksItem
  from ..models.ftm_dokument_pages_sanctions_item import FtmDokumentPagesSanctionsItem
  from ..models.ftm_dokument_pages_unknown_link_from import FtmDokumentPagesUnknownLinkFrom
  from ..models.ftm_dokument_pages_unknown_link_to import FtmDokumentPagesUnknownLinkTo





T = TypeVar("T", bound="FtmDokumentPages")



@_attrs_define
class FtmDokumentPages:
    """ See https://followthemoney.tech/explorer/schemata/Pages/ Currently here for experimentation which fields can be
    meaningfully filled.

        Attributes:
            file_name (str | Unset):
            title (str | Unset):
            mime_type (Mime | Unset):
            parent (str | Unset):
            pdf_hash (str | Unset):
            pages (list[FtmDokumentPages] | Unset):
            content_hash (str | Unset):
            author (str | Unset):
            generator (str | Unset):
            crawler (str | Unset):
            file_size (int | Unset):
            extension (str | Unset):
            encoding (str | Unset):
            body_text (str | Unset):
            message_id (str | Unset):
            language (str | Unset):
            translated_language (str | Unset):
            translated_text (str | Unset):
            date (datetime.datetime | Unset):
            authored_at (datetime.datetime | Unset):
            published_at (datetime.datetime | Unset):
            ancestors (list[FtmDokumentPagesAncestorsItem] | Unset):
            processing_status (str | Unset):
            processing_error (str | Unset):
            processing_agent (str | Unset):
            processed_at (datetime.datetime | Unset):
            proven (list[FtmDokumentPagesProvenItem] | Unset):
            name (str | Unset):
            alias (str | Unset):
            previous_name (str | Unset):
            weak_alias (str | Unset):
            country (str | Unset):
            summary (str | Unset):
            notes (str | Unset):
            description (str | Unset):
            source_url (str | Unset):
            publisher (str | Unset):
            publisher_url (str | Unset):
            aleph_url (str | Unset):
            wikipedia_url (str | Unset):
            wikidata_id (str | Unset):
            keywords (list[str] | Unset):
            topics (list[str] | Unset):
            address (str | Unset):
            address_entity (FtmDokumentPagesAddressEntity | Unset):
            program (str | Unset):
            program_id (str | Unset):
            proof (FtmDokumentPagesProof | Unset):
            index_text (str | Unset):
            created_at (datetime.datetime | Unset):
            modified_at (datetime.datetime | Unset):
            retrieved_at (datetime.datetime | Unset):
            detected_language (str | Unset):
            detected_country (str | Unset):
            names_mentioned (list[str] | Unset):
            people_mentioned (list[str] | Unset):
            companies_mentioned (list[str] | Unset):
            iban_mentioned (list[str] | Unset):
            ip_mentioned (list[str] | Unset):
            location_mentioned (list[str] | Unset):
            phone_mentioned (list[str] | Unset):
            email_mentioned (list[str] | Unset):
            proven_intervals (list[FtmDokumentPagesProvenIntervalsItem] | Unset):
            related_entities (list[FtmDokumentPagesRelatedEntitiesItem] | Unset):
            documented_by (FtmDokumentPagesDocumentedBy | Unset):
            note_entities (FtmDokumentPagesNoteEntities | Unset):
            sanctions (list[FtmDokumentPagesSanctionsItem] | Unset):
            candidate_similars (list[FtmDokumentPagesCandidateSimilarsItem] | Unset):
            match_similars (list[FtmDokumentPagesMatchSimilarsItem] | Unset):
            risks (list[FtmDokumentPagesRisksItem] | Unset):
            mentioned_entities (list[FtmDokumentPagesMentionedEntitiesItem] | Unset):
            unknown_link_to (FtmDokumentPagesUnknownLinkTo | Unset):
            unknown_link_from (FtmDokumentPagesUnknownLinkFrom | Unset):
            court_case (list[FtmDokumentPagesCourtCaseItem] | Unset):
     """

    file_name: str | Unset = UNSET
    title: str | Unset = UNSET
    mime_type: Mime | Unset = UNSET
    parent: str | Unset = UNSET
    pdf_hash: str | Unset = UNSET
    pages: list[FtmDokumentPages] | Unset = UNSET
    content_hash: str | Unset = UNSET
    author: str | Unset = UNSET
    generator: str | Unset = UNSET
    crawler: str | Unset = UNSET
    file_size: int | Unset = UNSET
    extension: str | Unset = UNSET
    encoding: str | Unset = UNSET
    body_text: str | Unset = UNSET
    message_id: str | Unset = UNSET
    language: str | Unset = UNSET
    translated_language: str | Unset = UNSET
    translated_text: str | Unset = UNSET
    date: datetime.datetime | Unset = UNSET
    authored_at: datetime.datetime | Unset = UNSET
    published_at: datetime.datetime | Unset = UNSET
    ancestors: list[FtmDokumentPagesAncestorsItem] | Unset = UNSET
    processing_status: str | Unset = UNSET
    processing_error: str | Unset = UNSET
    processing_agent: str | Unset = UNSET
    processed_at: datetime.datetime | Unset = UNSET
    proven: list[FtmDokumentPagesProvenItem] | Unset = UNSET
    name: str | Unset = UNSET
    alias: str | Unset = UNSET
    previous_name: str | Unset = UNSET
    weak_alias: str | Unset = UNSET
    country: str | Unset = UNSET
    summary: str | Unset = UNSET
    notes: str | Unset = UNSET
    description: str | Unset = UNSET
    source_url: str | Unset = UNSET
    publisher: str | Unset = UNSET
    publisher_url: str | Unset = UNSET
    aleph_url: str | Unset = UNSET
    wikipedia_url: str | Unset = UNSET
    wikidata_id: str | Unset = UNSET
    keywords: list[str] | Unset = UNSET
    topics: list[str] | Unset = UNSET
    address: str | Unset = UNSET
    address_entity: FtmDokumentPagesAddressEntity | Unset = UNSET
    program: str | Unset = UNSET
    program_id: str | Unset = UNSET
    proof: FtmDokumentPagesProof | Unset = UNSET
    index_text: str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    modified_at: datetime.datetime | Unset = UNSET
    retrieved_at: datetime.datetime | Unset = UNSET
    detected_language: str | Unset = UNSET
    detected_country: str | Unset = UNSET
    names_mentioned: list[str] | Unset = UNSET
    people_mentioned: list[str] | Unset = UNSET
    companies_mentioned: list[str] | Unset = UNSET
    iban_mentioned: list[str] | Unset = UNSET
    ip_mentioned: list[str] | Unset = UNSET
    location_mentioned: list[str] | Unset = UNSET
    phone_mentioned: list[str] | Unset = UNSET
    email_mentioned: list[str] | Unset = UNSET
    proven_intervals: list[FtmDokumentPagesProvenIntervalsItem] | Unset = UNSET
    related_entities: list[FtmDokumentPagesRelatedEntitiesItem] | Unset = UNSET
    documented_by: FtmDokumentPagesDocumentedBy | Unset = UNSET
    note_entities: FtmDokumentPagesNoteEntities | Unset = UNSET
    sanctions: list[FtmDokumentPagesSanctionsItem] | Unset = UNSET
    candidate_similars: list[FtmDokumentPagesCandidateSimilarsItem] | Unset = UNSET
    match_similars: list[FtmDokumentPagesMatchSimilarsItem] | Unset = UNSET
    risks: list[FtmDokumentPagesRisksItem] | Unset = UNSET
    mentioned_entities: list[FtmDokumentPagesMentionedEntitiesItem] | Unset = UNSET
    unknown_link_to: FtmDokumentPagesUnknownLinkTo | Unset = UNSET
    unknown_link_from: FtmDokumentPagesUnknownLinkFrom | Unset = UNSET
    court_case: list[FtmDokumentPagesCourtCaseItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.ftm_dokument_pages_address_entity import FtmDokumentPagesAddressEntity
        from ..models.ftm_dokument_pages_ancestors_item import FtmDokumentPagesAncestorsItem
        from ..models.ftm_dokument_pages_candidate_similars_item import FtmDokumentPagesCandidateSimilarsItem
        from ..models.ftm_dokument_pages_court_case_item import FtmDokumentPagesCourtCaseItem
        from ..models.ftm_dokument_pages_documented_by import FtmDokumentPagesDocumentedBy
        from ..models.ftm_dokument_pages_match_similars_item import FtmDokumentPagesMatchSimilarsItem
        from ..models.ftm_dokument_pages_mentioned_entities_item import FtmDokumentPagesMentionedEntitiesItem
        from ..models.ftm_dokument_pages_note_entities import FtmDokumentPagesNoteEntities
        from ..models.ftm_dokument_pages_proof import FtmDokumentPagesProof
        from ..models.ftm_dokument_pages_proven_intervals_item import FtmDokumentPagesProvenIntervalsItem
        from ..models.ftm_dokument_pages_proven_item import FtmDokumentPagesProvenItem
        from ..models.ftm_dokument_pages_related_entities_item import FtmDokumentPagesRelatedEntitiesItem
        from ..models.ftm_dokument_pages_risks_item import FtmDokumentPagesRisksItem
        from ..models.ftm_dokument_pages_sanctions_item import FtmDokumentPagesSanctionsItem
        from ..models.ftm_dokument_pages_unknown_link_from import FtmDokumentPagesUnknownLinkFrom
        from ..models.ftm_dokument_pages_unknown_link_to import FtmDokumentPagesUnknownLinkTo
        file_name = self.file_name

        title = self.title

        mime_type: str | Unset = UNSET
        if not isinstance(self.mime_type, Unset):
            mime_type = self.mime_type.value


        parent = self.parent

        pdf_hash = self.pdf_hash

        pages: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.pages, Unset):
            pages = []
            for pages_item_data in self.pages:
                pages_item = pages_item_data.to_dict()
                pages.append(pages_item)



        content_hash = self.content_hash

        author = self.author

        generator = self.generator

        crawler = self.crawler

        file_size = self.file_size

        extension = self.extension

        encoding = self.encoding

        body_text = self.body_text

        message_id = self.message_id

        language = self.language

        translated_language = self.translated_language

        translated_text = self.translated_text

        date: str | Unset = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        authored_at: str | Unset = UNSET
        if not isinstance(self.authored_at, Unset):
            authored_at = self.authored_at.isoformat()

        published_at: str | Unset = UNSET
        if not isinstance(self.published_at, Unset):
            published_at = self.published_at.isoformat()

        ancestors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.ancestors, Unset):
            ancestors = []
            for ancestors_item_data in self.ancestors:
                ancestors_item = ancestors_item_data.to_dict()
                ancestors.append(ancestors_item)



        processing_status = self.processing_status

        processing_error = self.processing_error

        processing_agent = self.processing_agent

        processed_at: str | Unset = UNSET
        if not isinstance(self.processed_at, Unset):
            processed_at = self.processed_at.isoformat()

        proven: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.proven, Unset):
            proven = []
            for proven_item_data in self.proven:
                proven_item = proven_item_data.to_dict()
                proven.append(proven_item)



        name = self.name

        alias = self.alias

        previous_name = self.previous_name

        weak_alias = self.weak_alias

        country = self.country

        summary = self.summary

        notes = self.notes

        description = self.description

        source_url = self.source_url

        publisher = self.publisher

        publisher_url = self.publisher_url

        aleph_url = self.aleph_url

        wikipedia_url = self.wikipedia_url

        wikidata_id = self.wikidata_id

        keywords: list[str] | Unset = UNSET
        if not isinstance(self.keywords, Unset):
            keywords = self.keywords



        topics: list[str] | Unset = UNSET
        if not isinstance(self.topics, Unset):
            topics = self.topics



        address = self.address

        address_entity: dict[str, Any] | Unset = UNSET
        if not isinstance(self.address_entity, Unset):
            address_entity = self.address_entity.to_dict()

        program = self.program

        program_id = self.program_id

        proof: dict[str, Any] | Unset = UNSET
        if not isinstance(self.proof, Unset):
            proof = self.proof.to_dict()

        index_text = self.index_text

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        modified_at: str | Unset = UNSET
        if not isinstance(self.modified_at, Unset):
            modified_at = self.modified_at.isoformat()

        retrieved_at: str | Unset = UNSET
        if not isinstance(self.retrieved_at, Unset):
            retrieved_at = self.retrieved_at.isoformat()

        detected_language = self.detected_language

        detected_country = self.detected_country

        names_mentioned: list[str] | Unset = UNSET
        if not isinstance(self.names_mentioned, Unset):
            names_mentioned = self.names_mentioned



        people_mentioned: list[str] | Unset = UNSET
        if not isinstance(self.people_mentioned, Unset):
            people_mentioned = self.people_mentioned



        companies_mentioned: list[str] | Unset = UNSET
        if not isinstance(self.companies_mentioned, Unset):
            companies_mentioned = self.companies_mentioned



        iban_mentioned: list[str] | Unset = UNSET
        if not isinstance(self.iban_mentioned, Unset):
            iban_mentioned = self.iban_mentioned



        ip_mentioned: list[str] | Unset = UNSET
        if not isinstance(self.ip_mentioned, Unset):
            ip_mentioned = self.ip_mentioned



        location_mentioned: list[str] | Unset = UNSET
        if not isinstance(self.location_mentioned, Unset):
            location_mentioned = self.location_mentioned



        phone_mentioned: list[str] | Unset = UNSET
        if not isinstance(self.phone_mentioned, Unset):
            phone_mentioned = self.phone_mentioned



        email_mentioned: list[str] | Unset = UNSET
        if not isinstance(self.email_mentioned, Unset):
            email_mentioned = self.email_mentioned



        proven_intervals: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.proven_intervals, Unset):
            proven_intervals = []
            for proven_intervals_item_data in self.proven_intervals:
                proven_intervals_item = proven_intervals_item_data.to_dict()
                proven_intervals.append(proven_intervals_item)



        related_entities: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.related_entities, Unset):
            related_entities = []
            for related_entities_item_data in self.related_entities:
                related_entities_item = related_entities_item_data.to_dict()
                related_entities.append(related_entities_item)



        documented_by: dict[str, Any] | Unset = UNSET
        if not isinstance(self.documented_by, Unset):
            documented_by = self.documented_by.to_dict()

        note_entities: dict[str, Any] | Unset = UNSET
        if not isinstance(self.note_entities, Unset):
            note_entities = self.note_entities.to_dict()

        sanctions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sanctions, Unset):
            sanctions = []
            for sanctions_item_data in self.sanctions:
                sanctions_item = sanctions_item_data.to_dict()
                sanctions.append(sanctions_item)



        candidate_similars: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.candidate_similars, Unset):
            candidate_similars = []
            for candidate_similars_item_data in self.candidate_similars:
                candidate_similars_item = candidate_similars_item_data.to_dict()
                candidate_similars.append(candidate_similars_item)



        match_similars: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.match_similars, Unset):
            match_similars = []
            for match_similars_item_data in self.match_similars:
                match_similars_item = match_similars_item_data.to_dict()
                match_similars.append(match_similars_item)



        risks: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.risks, Unset):
            risks = []
            for risks_item_data in self.risks:
                risks_item = risks_item_data.to_dict()
                risks.append(risks_item)



        mentioned_entities: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.mentioned_entities, Unset):
            mentioned_entities = []
            for mentioned_entities_item_data in self.mentioned_entities:
                mentioned_entities_item = mentioned_entities_item_data.to_dict()
                mentioned_entities.append(mentioned_entities_item)



        unknown_link_to: dict[str, Any] | Unset = UNSET
        if not isinstance(self.unknown_link_to, Unset):
            unknown_link_to = self.unknown_link_to.to_dict()

        unknown_link_from: dict[str, Any] | Unset = UNSET
        if not isinstance(self.unknown_link_from, Unset):
            unknown_link_from = self.unknown_link_from.to_dict()

        court_case: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.court_case, Unset):
            court_case = []
            for court_case_item_data in self.court_case:
                court_case_item = court_case_item_data.to_dict()
                court_case.append(court_case_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if title is not UNSET:
            field_dict["title"] = title
        if mime_type is not UNSET:
            field_dict["mimeType"] = mime_type
        if parent is not UNSET:
            field_dict["parent"] = parent
        if pdf_hash is not UNSET:
            field_dict["pdfHash"] = pdf_hash
        if pages is not UNSET:
            field_dict["pages"] = pages
        if content_hash is not UNSET:
            field_dict["contentHash"] = content_hash
        if author is not UNSET:
            field_dict["author"] = author
        if generator is not UNSET:
            field_dict["generator"] = generator
        if crawler is not UNSET:
            field_dict["crawler"] = crawler
        if file_size is not UNSET:
            field_dict["fileSize"] = file_size
        if extension is not UNSET:
            field_dict["extension"] = extension
        if encoding is not UNSET:
            field_dict["encoding"] = encoding
        if body_text is not UNSET:
            field_dict["bodyText"] = body_text
        if message_id is not UNSET:
            field_dict["messageId"] = message_id
        if language is not UNSET:
            field_dict["language"] = language
        if translated_language is not UNSET:
            field_dict["translatedLanguage"] = translated_language
        if translated_text is not UNSET:
            field_dict["translatedText"] = translated_text
        if date is not UNSET:
            field_dict["date"] = date
        if authored_at is not UNSET:
            field_dict["authoredAt"] = authored_at
        if published_at is not UNSET:
            field_dict["publishedAt"] = published_at
        if ancestors is not UNSET:
            field_dict["ancestors"] = ancestors
        if processing_status is not UNSET:
            field_dict["processingStatus"] = processing_status
        if processing_error is not UNSET:
            field_dict["processingError"] = processing_error
        if processing_agent is not UNSET:
            field_dict["processingAgent"] = processing_agent
        if processed_at is not UNSET:
            field_dict["processedAt"] = processed_at
        if proven is not UNSET:
            field_dict["proven"] = proven
        if name is not UNSET:
            field_dict["name"] = name
        if alias is not UNSET:
            field_dict["alias"] = alias
        if previous_name is not UNSET:
            field_dict["previousName"] = previous_name
        if weak_alias is not UNSET:
            field_dict["weakAlias"] = weak_alias
        if country is not UNSET:
            field_dict["country"] = country
        if summary is not UNSET:
            field_dict["summary"] = summary
        if notes is not UNSET:
            field_dict["notes"] = notes
        if description is not UNSET:
            field_dict["description"] = description
        if source_url is not UNSET:
            field_dict["sourceUrl"] = source_url
        if publisher is not UNSET:
            field_dict["publisher"] = publisher
        if publisher_url is not UNSET:
            field_dict["publisherUrl"] = publisher_url
        if aleph_url is not UNSET:
            field_dict["alephUrl"] = aleph_url
        if wikipedia_url is not UNSET:
            field_dict["wikipediaUrl"] = wikipedia_url
        if wikidata_id is not UNSET:
            field_dict["wikidataId"] = wikidata_id
        if keywords is not UNSET:
            field_dict["keywords"] = keywords
        if topics is not UNSET:
            field_dict["topics"] = topics
        if address is not UNSET:
            field_dict["address"] = address
        if address_entity is not UNSET:
            field_dict["addressEntity"] = address_entity
        if program is not UNSET:
            field_dict["program"] = program
        if program_id is not UNSET:
            field_dict["programId"] = program_id
        if proof is not UNSET:
            field_dict["proof"] = proof
        if index_text is not UNSET:
            field_dict["indexText"] = index_text
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if retrieved_at is not UNSET:
            field_dict["retrievedAt"] = retrieved_at
        if detected_language is not UNSET:
            field_dict["detectedLanguage"] = detected_language
        if detected_country is not UNSET:
            field_dict["detectedCountry"] = detected_country
        if names_mentioned is not UNSET:
            field_dict["namesMentioned"] = names_mentioned
        if people_mentioned is not UNSET:
            field_dict["peopleMentioned"] = people_mentioned
        if companies_mentioned is not UNSET:
            field_dict["companiesMentioned"] = companies_mentioned
        if iban_mentioned is not UNSET:
            field_dict["ibanMentioned"] = iban_mentioned
        if ip_mentioned is not UNSET:
            field_dict["ipMentioned"] = ip_mentioned
        if location_mentioned is not UNSET:
            field_dict["locationMentioned"] = location_mentioned
        if phone_mentioned is not UNSET:
            field_dict["phoneMentioned"] = phone_mentioned
        if email_mentioned is not UNSET:
            field_dict["emailMentioned"] = email_mentioned
        if proven_intervals is not UNSET:
            field_dict["provenIntervals"] = proven_intervals
        if related_entities is not UNSET:
            field_dict["relatedEntities"] = related_entities
        if documented_by is not UNSET:
            field_dict["documentedBy"] = documented_by
        if note_entities is not UNSET:
            field_dict["noteEntities"] = note_entities
        if sanctions is not UNSET:
            field_dict["sanctions"] = sanctions
        if candidate_similars is not UNSET:
            field_dict["candidateSimilars"] = candidate_similars
        if match_similars is not UNSET:
            field_dict["matchSimilars"] = match_similars
        if risks is not UNSET:
            field_dict["risks"] = risks
        if mentioned_entities is not UNSET:
            field_dict["mentionedEntities"] = mentioned_entities
        if unknown_link_to is not UNSET:
            field_dict["unknownLinkTo"] = unknown_link_to
        if unknown_link_from is not UNSET:
            field_dict["unknownLinkFrom"] = unknown_link_from
        if court_case is not UNSET:
            field_dict["courtCase"] = court_case

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ftm_dokument_pages_address_entity import FtmDokumentPagesAddressEntity
        from ..models.ftm_dokument_pages_ancestors_item import FtmDokumentPagesAncestorsItem
        from ..models.ftm_dokument_pages_candidate_similars_item import FtmDokumentPagesCandidateSimilarsItem
        from ..models.ftm_dokument_pages_court_case_item import FtmDokumentPagesCourtCaseItem
        from ..models.ftm_dokument_pages_documented_by import FtmDokumentPagesDocumentedBy
        from ..models.ftm_dokument_pages_match_similars_item import FtmDokumentPagesMatchSimilarsItem
        from ..models.ftm_dokument_pages_mentioned_entities_item import FtmDokumentPagesMentionedEntitiesItem
        from ..models.ftm_dokument_pages_note_entities import FtmDokumentPagesNoteEntities
        from ..models.ftm_dokument_pages_proof import FtmDokumentPagesProof
        from ..models.ftm_dokument_pages_proven_intervals_item import FtmDokumentPagesProvenIntervalsItem
        from ..models.ftm_dokument_pages_proven_item import FtmDokumentPagesProvenItem
        from ..models.ftm_dokument_pages_related_entities_item import FtmDokumentPagesRelatedEntitiesItem
        from ..models.ftm_dokument_pages_risks_item import FtmDokumentPagesRisksItem
        from ..models.ftm_dokument_pages_sanctions_item import FtmDokumentPagesSanctionsItem
        from ..models.ftm_dokument_pages_unknown_link_from import FtmDokumentPagesUnknownLinkFrom
        from ..models.ftm_dokument_pages_unknown_link_to import FtmDokumentPagesUnknownLinkTo
        d = dict(src_dict)
        file_name = d.pop("fileName", UNSET)

        title = d.pop("title", UNSET)

        _mime_type = d.pop("mimeType", UNSET)
        mime_type: Mime | Unset
        if isinstance(_mime_type,  Unset):
            mime_type = UNSET
        else:
            mime_type = Mime(_mime_type)




        parent = d.pop("parent", UNSET)

        pdf_hash = d.pop("pdfHash", UNSET)

        _pages = d.pop("pages", UNSET)
        pages: list[FtmDokumentPages] | Unset = UNSET
        if _pages is not UNSET:
            pages = []
            for pages_item_data in _pages:
                pages_item = FtmDokumentPages.from_dict(pages_item_data)



                pages.append(pages_item)


        content_hash = d.pop("contentHash", UNSET)

        author = d.pop("author", UNSET)

        generator = d.pop("generator", UNSET)

        crawler = d.pop("crawler", UNSET)

        file_size = d.pop("fileSize", UNSET)

        extension = d.pop("extension", UNSET)

        encoding = d.pop("encoding", UNSET)

        body_text = d.pop("bodyText", UNSET)

        message_id = d.pop("messageId", UNSET)

        language = d.pop("language", UNSET)

        translated_language = d.pop("translatedLanguage", UNSET)

        translated_text = d.pop("translatedText", UNSET)

        _date = d.pop("date", UNSET)
        date: datetime.datetime | Unset
        if isinstance(_date,  Unset):
            date = UNSET
        else:
            date = isoparse(_date)




        _authored_at = d.pop("authoredAt", UNSET)
        authored_at: datetime.datetime | Unset
        if isinstance(_authored_at,  Unset):
            authored_at = UNSET
        else:
            authored_at = isoparse(_authored_at)




        _published_at = d.pop("publishedAt", UNSET)
        published_at: datetime.datetime | Unset
        if isinstance(_published_at,  Unset):
            published_at = UNSET
        else:
            published_at = isoparse(_published_at)




        _ancestors = d.pop("ancestors", UNSET)
        ancestors: list[FtmDokumentPagesAncestorsItem] | Unset = UNSET
        if _ancestors is not UNSET:
            ancestors = []
            for ancestors_item_data in _ancestors:
                ancestors_item = FtmDokumentPagesAncestorsItem.from_dict(ancestors_item_data)



                ancestors.append(ancestors_item)


        processing_status = d.pop("processingStatus", UNSET)

        processing_error = d.pop("processingError", UNSET)

        processing_agent = d.pop("processingAgent", UNSET)

        _processed_at = d.pop("processedAt", UNSET)
        processed_at: datetime.datetime | Unset
        if isinstance(_processed_at,  Unset):
            processed_at = UNSET
        else:
            processed_at = isoparse(_processed_at)




        _proven = d.pop("proven", UNSET)
        proven: list[FtmDokumentPagesProvenItem] | Unset = UNSET
        if _proven is not UNSET:
            proven = []
            for proven_item_data in _proven:
                proven_item = FtmDokumentPagesProvenItem.from_dict(proven_item_data)



                proven.append(proven_item)


        name = d.pop("name", UNSET)

        alias = d.pop("alias", UNSET)

        previous_name = d.pop("previousName", UNSET)

        weak_alias = d.pop("weakAlias", UNSET)

        country = d.pop("country", UNSET)

        summary = d.pop("summary", UNSET)

        notes = d.pop("notes", UNSET)

        description = d.pop("description", UNSET)

        source_url = d.pop("sourceUrl", UNSET)

        publisher = d.pop("publisher", UNSET)

        publisher_url = d.pop("publisherUrl", UNSET)

        aleph_url = d.pop("alephUrl", UNSET)

        wikipedia_url = d.pop("wikipediaUrl", UNSET)

        wikidata_id = d.pop("wikidataId", UNSET)

        keywords = cast(list[str], d.pop("keywords", UNSET))


        topics = cast(list[str], d.pop("topics", UNSET))


        address = d.pop("address", UNSET)

        _address_entity = d.pop("addressEntity", UNSET)
        address_entity: FtmDokumentPagesAddressEntity | Unset
        if isinstance(_address_entity,  Unset):
            address_entity = UNSET
        else:
            address_entity = FtmDokumentPagesAddressEntity.from_dict(_address_entity)




        program = d.pop("program", UNSET)

        program_id = d.pop("programId", UNSET)

        _proof = d.pop("proof", UNSET)
        proof: FtmDokumentPagesProof | Unset
        if isinstance(_proof,  Unset):
            proof = UNSET
        else:
            proof = FtmDokumentPagesProof.from_dict(_proof)




        index_text = d.pop("indexText", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _modified_at = d.pop("modifiedAt", UNSET)
        modified_at: datetime.datetime | Unset
        if isinstance(_modified_at,  Unset):
            modified_at = UNSET
        else:
            modified_at = isoparse(_modified_at)




        _retrieved_at = d.pop("retrievedAt", UNSET)
        retrieved_at: datetime.datetime | Unset
        if isinstance(_retrieved_at,  Unset):
            retrieved_at = UNSET
        else:
            retrieved_at = isoparse(_retrieved_at)




        detected_language = d.pop("detectedLanguage", UNSET)

        detected_country = d.pop("detectedCountry", UNSET)

        names_mentioned = cast(list[str], d.pop("namesMentioned", UNSET))


        people_mentioned = cast(list[str], d.pop("peopleMentioned", UNSET))


        companies_mentioned = cast(list[str], d.pop("companiesMentioned", UNSET))


        iban_mentioned = cast(list[str], d.pop("ibanMentioned", UNSET))


        ip_mentioned = cast(list[str], d.pop("ipMentioned", UNSET))


        location_mentioned = cast(list[str], d.pop("locationMentioned", UNSET))


        phone_mentioned = cast(list[str], d.pop("phoneMentioned", UNSET))


        email_mentioned = cast(list[str], d.pop("emailMentioned", UNSET))


        _proven_intervals = d.pop("provenIntervals", UNSET)
        proven_intervals: list[FtmDokumentPagesProvenIntervalsItem] | Unset = UNSET
        if _proven_intervals is not UNSET:
            proven_intervals = []
            for proven_intervals_item_data in _proven_intervals:
                proven_intervals_item = FtmDokumentPagesProvenIntervalsItem.from_dict(proven_intervals_item_data)



                proven_intervals.append(proven_intervals_item)


        _related_entities = d.pop("relatedEntities", UNSET)
        related_entities: list[FtmDokumentPagesRelatedEntitiesItem] | Unset = UNSET
        if _related_entities is not UNSET:
            related_entities = []
            for related_entities_item_data in _related_entities:
                related_entities_item = FtmDokumentPagesRelatedEntitiesItem.from_dict(related_entities_item_data)



                related_entities.append(related_entities_item)


        _documented_by = d.pop("documentedBy", UNSET)
        documented_by: FtmDokumentPagesDocumentedBy | Unset
        if isinstance(_documented_by,  Unset):
            documented_by = UNSET
        else:
            documented_by = FtmDokumentPagesDocumentedBy.from_dict(_documented_by)




        _note_entities = d.pop("noteEntities", UNSET)
        note_entities: FtmDokumentPagesNoteEntities | Unset
        if isinstance(_note_entities,  Unset):
            note_entities = UNSET
        else:
            note_entities = FtmDokumentPagesNoteEntities.from_dict(_note_entities)




        _sanctions = d.pop("sanctions", UNSET)
        sanctions: list[FtmDokumentPagesSanctionsItem] | Unset = UNSET
        if _sanctions is not UNSET:
            sanctions = []
            for sanctions_item_data in _sanctions:
                sanctions_item = FtmDokumentPagesSanctionsItem.from_dict(sanctions_item_data)



                sanctions.append(sanctions_item)


        _candidate_similars = d.pop("candidateSimilars", UNSET)
        candidate_similars: list[FtmDokumentPagesCandidateSimilarsItem] | Unset = UNSET
        if _candidate_similars is not UNSET:
            candidate_similars = []
            for candidate_similars_item_data in _candidate_similars:
                candidate_similars_item = FtmDokumentPagesCandidateSimilarsItem.from_dict(candidate_similars_item_data)



                candidate_similars.append(candidate_similars_item)


        _match_similars = d.pop("matchSimilars", UNSET)
        match_similars: list[FtmDokumentPagesMatchSimilarsItem] | Unset = UNSET
        if _match_similars is not UNSET:
            match_similars = []
            for match_similars_item_data in _match_similars:
                match_similars_item = FtmDokumentPagesMatchSimilarsItem.from_dict(match_similars_item_data)



                match_similars.append(match_similars_item)


        _risks = d.pop("risks", UNSET)
        risks: list[FtmDokumentPagesRisksItem] | Unset = UNSET
        if _risks is not UNSET:
            risks = []
            for risks_item_data in _risks:
                risks_item = FtmDokumentPagesRisksItem.from_dict(risks_item_data)



                risks.append(risks_item)


        _mentioned_entities = d.pop("mentionedEntities", UNSET)
        mentioned_entities: list[FtmDokumentPagesMentionedEntitiesItem] | Unset = UNSET
        if _mentioned_entities is not UNSET:
            mentioned_entities = []
            for mentioned_entities_item_data in _mentioned_entities:
                mentioned_entities_item = FtmDokumentPagesMentionedEntitiesItem.from_dict(mentioned_entities_item_data)



                mentioned_entities.append(mentioned_entities_item)


        _unknown_link_to = d.pop("unknownLinkTo", UNSET)
        unknown_link_to: FtmDokumentPagesUnknownLinkTo | Unset
        if isinstance(_unknown_link_to,  Unset):
            unknown_link_to = UNSET
        else:
            unknown_link_to = FtmDokumentPagesUnknownLinkTo.from_dict(_unknown_link_to)




        _unknown_link_from = d.pop("unknownLinkFrom", UNSET)
        unknown_link_from: FtmDokumentPagesUnknownLinkFrom | Unset
        if isinstance(_unknown_link_from,  Unset):
            unknown_link_from = UNSET
        else:
            unknown_link_from = FtmDokumentPagesUnknownLinkFrom.from_dict(_unknown_link_from)




        _court_case = d.pop("courtCase", UNSET)
        court_case: list[FtmDokumentPagesCourtCaseItem] | Unset = UNSET
        if _court_case is not UNSET:
            court_case = []
            for court_case_item_data in _court_case:
                court_case_item = FtmDokumentPagesCourtCaseItem.from_dict(court_case_item_data)



                court_case.append(court_case_item)


        ftm_dokument_pages = cls(
            file_name=file_name,
            title=title,
            mime_type=mime_type,
            parent=parent,
            pdf_hash=pdf_hash,
            pages=pages,
            content_hash=content_hash,
            author=author,
            generator=generator,
            crawler=crawler,
            file_size=file_size,
            extension=extension,
            encoding=encoding,
            body_text=body_text,
            message_id=message_id,
            language=language,
            translated_language=translated_language,
            translated_text=translated_text,
            date=date,
            authored_at=authored_at,
            published_at=published_at,
            ancestors=ancestors,
            processing_status=processing_status,
            processing_error=processing_error,
            processing_agent=processing_agent,
            processed_at=processed_at,
            proven=proven,
            name=name,
            alias=alias,
            previous_name=previous_name,
            weak_alias=weak_alias,
            country=country,
            summary=summary,
            notes=notes,
            description=description,
            source_url=source_url,
            publisher=publisher,
            publisher_url=publisher_url,
            aleph_url=aleph_url,
            wikipedia_url=wikipedia_url,
            wikidata_id=wikidata_id,
            keywords=keywords,
            topics=topics,
            address=address,
            address_entity=address_entity,
            program=program,
            program_id=program_id,
            proof=proof,
            index_text=index_text,
            created_at=created_at,
            modified_at=modified_at,
            retrieved_at=retrieved_at,
            detected_language=detected_language,
            detected_country=detected_country,
            names_mentioned=names_mentioned,
            people_mentioned=people_mentioned,
            companies_mentioned=companies_mentioned,
            iban_mentioned=iban_mentioned,
            ip_mentioned=ip_mentioned,
            location_mentioned=location_mentioned,
            phone_mentioned=phone_mentioned,
            email_mentioned=email_mentioned,
            proven_intervals=proven_intervals,
            related_entities=related_entities,
            documented_by=documented_by,
            note_entities=note_entities,
            sanctions=sanctions,
            candidate_similars=candidate_similars,
            match_similars=match_similars,
            risks=risks,
            mentioned_entities=mentioned_entities,
            unknown_link_to=unknown_link_to,
            unknown_link_from=unknown_link_from,
            court_case=court_case,
        )


        ftm_dokument_pages.additional_properties = d
        return ftm_dokument_pages

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
