from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text
import json
import re


class Fitch(ArticleScraper):
    def __init__(self):
        self.url = "https://api.fitchratings.com"

    async def query_gql(self):
        params = {
            "operationName": "Search",
            "variables": {
                "item": "ALL",
                "term": "",
                "filter": {"language": ["English"]},
                "sort": "",
                "dateRange": "",
                "offset": 0,
                "limit": 24,
            },
            "query": "query Search($item: SearchItem, $term: String!, $filter: SearchFilterInput, $sort: String, $dateRange: String, $offset: Int, $limit: Int) {\n  search(item: $item, term: $term, filter: $filter, sort: $sort, dateRange: $dateRange, offset: $offset, limit: $limit) {\n    totalResearchHits\n    totalRacsHits\n    totalEntityHits\n    totalIssueHits\n    totalVideoHits\n    totalEventHits\n    totalAudioHits\n    totalPageHits\n    totalHits\n    research {\n      docType\n      marketing {\n        contentAccessType {\n          name\n          slug\n          __typename\n        }\n        language {\n          name\n          slug\n          __typename\n        }\n        analysts {\n          firstName\n          lastName\n          role\n          sequenceNumber\n          type\n          __typename\n        }\n        countries {\n          name\n          slug\n          __typename\n        }\n        sectors {\n          name\n          slug\n          __typename\n        }\n        __typename\n      }\n      title\n      permalink\n      abstract\n      reportType\n      publishedDate\n      __typename\n    }\n    racs {\n      docType\n      marketing {\n        contentAccessType {\n          name\n          slug\n          __typename\n        }\n        language {\n          name\n          slug\n          __typename\n        }\n        analysts {\n          firstName\n          lastName\n          role\n          sequenceNumber\n          type\n          __typename\n        }\n        countries {\n          name\n          slug\n          __typename\n        }\n        sectors {\n          name\n          slug\n          __typename\n        }\n        __typename\n      }\n      title\n      permalink\n      abstract\n      reportType\n      publishedDate\n      __typename\n    }\n    entity {\n      marketing {\n        analysts {\n          firstName\n          lastName\n          role\n          sequenceNumber\n          type\n          __typename\n        }\n        countries {\n          name\n          slug\n          __typename\n        }\n        sectors {\n          name\n          slug\n          __typename\n        }\n        __typename\n      }\n      name\n      ultimateParent\n      ratings {\n        orangeDisplay\n        ratingCode\n        ratingAlertCode\n        ratingActionDescription\n        ratingAlertDescription\n        ratingTypeDescription\n        ratingEffectiveDate\n        __typename\n      }\n      permalink\n      __typename\n    }\n    issue {\n      permalink\n      issue\n      issueName\n      issuer\n      entityName\n      debtLevel\n      deal\n      className\n      subClass\n      transaction {\n        description\n        id\n        securityList {\n          typeDescription\n          __typename\n        }\n        __typename\n      }\n      ratingDate\n      maturityDate\n      cusip\n      isin\n      originalAmount\n      currency\n      couponRate\n      subgroupName\n      ratableTypeDescription\n      commercialPaperType\n      marketing {\n        analysts {\n          firstName\n          lastName\n          type\n          sequenceNumber\n          __typename\n        }\n        countries {\n          name\n          slug\n          __typename\n        }\n        sectors {\n          name\n          slug\n          __typename\n        }\n        __typename\n      }\n      ratings {\n        orangeDisplay\n        ratableName\n        ratingActionDescription\n        ratingAlertCode\n        ratingAlertDescription\n        ratingCode\n        ratingEffectiveDate\n        ratingLocalActionDescription\n        ratingLocalValue\n        ratingTypeDescription\n        ratingTypeId\n        recoveryEstimate\n        recoveryRatingValue\n        solicitFlag\n        sortOrder\n        filterRatingType\n        filterNationalRatingType\n        filterInvestmentGradeType\n        __typename\n      }\n      __typename\n    }\n    page {\n      title\n      slug\n      image {\n        poster\n        thumbnail\n        __typename\n      }\n      __typename\n    }\n    totalHits\n    __typename\n  }\n}\n",
        }
        resp = await self._post_json("/", json=params)
        resp_json = json.loads(resp)["data"]["search"]
        headlines = []
        for group in ["research", "racs"]:
            for item in resp_json[group]:
                title = clean_html_text(item["title"])
                text = clean_html_text(item["abstract"])
                url = "https://www.fitchratings.com/" + item["permalink"]
                headlines.append((url, title, text))
        return headlines

    async def read_latest_headlines(self):
        headlines = []
        try:
            index_html = await self._get("/news-releases/news-releases-list/")
            headlines.extend(await self.query_gql())
        except KeyError:
            pass
        return "fitch", headlines
