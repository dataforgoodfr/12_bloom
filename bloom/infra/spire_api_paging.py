from typing import Any

from gql import Client, gql

from bloom.logger import logger


class Paging:
    def __init__(self, response: dict[str, Any] = None) -> None:
        self._response = response

    def get_pageinfo_elements(self) -> tuple[str, bool]:
        """Gets the elements helpful for Paging
        Returns:
            endcursor(str) - pageinfo.endcursor value
            hasnext(bool) - pageinfo.hasnext value
        """
        response = self._response
        if not response:
            logger.error("Did not get response, can't get paging information")
            raise TypeError
        pageinfo = response["vessels"]["pageInfo"]
        endcursor: str = pageinfo["endCursor"]
        hasnextpage: bool = pageinfo["hasNextPage"]
        return endcursor, hasnextpage

    def _should_stop_paging(self) -> bool:
        endcursor, hasnextpage = self.get_pageinfo_elements()
        if endcursor and hasnextpage:
            return False
        if not hasnextpage or endcursor is None:
            return True
        return None

    def get_response(self) -> dict[str, Any]:
        return self._response

    def page_and_get_response(
        self,
        client: Client,
        query: str,
    ) -> tuple[dict[str, Any], bool]:
        """
        Args:
            client: gql client
            query: str query string
            hasNextPage: bool optional - paging element, is there a next page - NOT HERE
        Returns:
            response: dict service response to query
            hasNextPage: bool paging element, is there a next page
        """
        if not self._response:
            try:
                self._response = client.execute(gql(query))
            except BaseException:
                logger.exception("Execution of the query failed")
                raise

        if self._should_stop_paging():
            return self._response
        # there is more, so page
        endcursor, hasnextpage = self.get_pageinfo_elements()
        if endcursor:
            insert_text = f',after: "{endcursor}" '
        else:
            logger.info(f"Error no endcursor {endcursor}")
            hasnextpage = False
            return self._response, hasnextpage
        query = self.insert_into_query_header(query=query, insert_text=insert_text)
        try:
            self._response = client.execute(gql(query))
        except BaseException as e:
            logger.warning(e)
            try:  # Try again as there could be internal errors from time to time
                self._response = client.execute(gql(query))
            except BaseException as e:
                self._response = False

        return self._response, hasnextpage

    def insert_into_query_header(query, insert_text: str = "") -> str:
        """Insert text into query header
        Args:
            query(str) - query string
            insert_text(str) - text to insert
        Returns
            new_query(str) - text with insert
        """
        if ")" in query:
            loc = query.find(")")
            # remove the existing )
            tmp: str = query.replace(")", "")
            # add paging elements where the ) once was .. + 1 for some spacing in case
            beginning: str = tmp[:loc]
            end: str = tmp[loc:]
            return beginning + " " + insert_text + " ) " + end
        return query
