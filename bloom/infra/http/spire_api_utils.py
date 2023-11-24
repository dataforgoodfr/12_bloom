from typing import Any

from gql import Client, gql

from bloom.logger import logger


class Paging:
    def __init__(self, vessel_list: list[str] = None) -> None:
        self._vessel_list = vessel_list

    def get_pageinfo_elements(self, response: dict[str, Any]) -> tuple[str, bool]:
        """Gets the elements helpful for Paging
        Returns:
            endcursor(str) - pageinfo.endcursor value
            hasnext(bool) - pageinfo.hasnext value
        """
        if not response:
            logger.error("Did not get response, can't get paging information")
            raise TypeError
        pageinfo = response["vessels"]["pageInfo"]
        endcursor: str = pageinfo["endCursor"]
        hasnextpage: bool = pageinfo["hasNextPage"]
        return endcursor, hasnextpage

    def _should_stop_paging(self, endcursor: str, hasnextpage: bool) -> bool:
        if endcursor and hasnextpage:
            return False
        if not hasnextpage or endcursor is None:
            return True

        return None

    def page_and_get_response(
        self,
        client: Client,
        query: str,
    ) -> dict[str, Any]:
        """
        Args:
            client: gql client
            query: str query string
            hasNextPage: bool optional - paging element, is there a next page - NOT HERE
        Returns:
            response: dict service response to query
        """
        try:
            response = client.execute(gql(query))
        except BaseException:
            logger.exception("Execution of the query failed")
            raise

        self.vessel_list = response["vessels"]["nodes"]
        endcursor, hasnextpage = self.get_pageinfo_elements(response)

        # there is more, so page
        initial_query = query
        while not self._should_stop_paging(endcursor, hasnextpage):
            response = None
            query = self.insert_into_query_header(initial_query, endcursor)
            try:
                response = client.execute(gql(query))
            except BaseException as e:
                logger.warning(e)
                # Try again as there could be internal errors from time to time
                response = client.execute(gql(query))

            self.vessel_list += response["vessels"]["nodes"]
            endcursor, hasnextpage = self.get_pageinfo_elements(response)
        logger.info(f"Number of vessel scrapped from Spire {len(self.vessel_list)}")
        return self.vessel_list

    def insert_into_query_header(self, query: str, endcursor: str = "") -> str:
        """Insert text into query header
        Args:
            query(str) - query string
            insert_text(str) - text to insert
        Returns
            new_query(str) - text with insert
        """
        insert_text = f',after: "{endcursor}" '
        if ")" in query:
            loc = query.find(")")
            # remove the existing )
            tmp: str = query.replace(")", "")
            # add paging elements where the ) once was .. + 1 for some spacing in case
            beginning: str = tmp[:loc]
            end: str = tmp[loc:]
            return beginning + " " + insert_text + " ) " + end
        return query
