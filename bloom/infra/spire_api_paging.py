from gql import gql

from bloom.logger import logger


class Paging:
    def __init__(self, response=None) -> None:
        self._response = response

    def get_pageInfo_elements(self):
        """Gets the elements helpful for Paging
        Returns:
            endCursor(str) - pageInfo.endCursor value
            hasNext(bool) - pageInfo.hasNext value
        """
        response = self._response
        if not response:
            logger.error("Did not get response, can't get paging information")
            raise Exception
        pageInfo = response["vessels"]["pageInfo"]
        endCursor: str = pageInfo["endCursor"]
        hasNextPage: bool = pageInfo["hasNextPage"]
        return endCursor, hasNextPage

    def _should_stop_paging(self):
        endCursor, hasNextPage = self.get_pageInfo_elements()
        if endCursor and hasNextPage:
            return False
        elif not hasNextPage or endCursor is None:
            return True

    def get_response(self):
        return self._response

    def page_and_get_response(self, client, query):
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
            except BaseException as e:
                logger.error(e)
                raise

        if self._should_stop_paging():
            hasNextPage = False
            return self._response, hasNextPage
        else:
            # there is more, so page
            endCursor, hasNextPage = self.get_pageInfo_elements()
            if endCursor:
                insert_text = f',after: "{endCursor}" '
            else:
                logger.info(f"Error no endCursor {endCursor}")
                hasNextPage = False
                return self._response, hasNextPage
            query = self.insert_into_query_header(query=query, insert_text=insert_text)
            try:
                self._response = client.execute(gql(query))
            except BaseException as e:
                logger.warning(e)
                try:  # Try again as there could be internal errors from time to time
                    self._response = client.execute(gql(query))
                except BaseException as e:
                    self._response = False

            return self._response, hasNextPage

    def insert_into_query_header(query, insert_text=""):
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
            new_query = beginning + " " + insert_text + " ) " + end
        else:
            return query
        return new_query
