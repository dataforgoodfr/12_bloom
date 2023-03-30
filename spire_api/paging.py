from loguru import logger
from gql import gql
import helpers


class Paging(object):

    def __init__(self, response=None):
        self._response = response

    def get_pageInfo_elements(self):
        """ Gets the elements helpful for Paging
        Returns:
            endCursor(str) - pageInfo.endCursor value
            hasNext(bool) - pageInfo.hasNext value
        """
        response = self._response
        if not response:
            logger.error("Did not get response, can't get paging information")
            raise Exception
        pageInfo = response['vessels']['pageInfo']
        endCursor: str = pageInfo['endCursor']
        hasNextPage: bool = pageInfo['hasNextPage']
        return endCursor, hasNextPage

    def _should_stop_paging(self):
        endCursor, hasNextPage = self.get_pageInfo_elements()
        if endCursor and hasNextPage:
            return False
        elif not hasNextPage or endCursor is NULL:
            return True

    def get_response(self):
        return self._response

    def page_and_get_response(self, client, query):
        """
        Args:
            client: gql client
            query: str query string
            hasNextPage: bool optional - paging element, is there a next page -- NOT HERE
        Returns:
            response: dict service response to query
            hasNextPage: bool paging element, is there a next page
        """
        if not self._response:
            try:
                # print(query)
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
                logger.info(f'Error no endCursor {endCursor}')
                hasNextPage = False
                return self._response, hasNextPage
            query = helpers.insert_into_query_header(query=query, insert_text=insert_text)
            try:
                # print(query)
                self._response = client.execute(gql(query))
            except BaseException as e:
                logger.warning(e)
                try: # Try again as there could be internal errors from time to time
                    # print(query)
                    self._response = client.execute(gql(query))
                except BaseException as e:
                    self._response = False

            return self._response, hasNextPage

    def start_paging(self, client, query_text):
        """
        Args:
            client: gql client
            query_text:  query to execute
        Returns:
            Yields response (dict)
        """
        page_count: int = 0
        responses: list = list()  # to help with error reporting of last response
        while True:
            response: dict = dict()
            hasNextPage: bool = False
            try:
                response, hasNextPage = self.page_and_get_response(client, query_text)
                responses.append(response)
            except BaseException as e:
                logger.error(e)
                self._detailed_error(responses, page_count, hasNextPage)
                raise

            if not response and hasNextPage:
                self._detailed_error(responses, page_count, hasNextPage)
                assert False
            elif not hasNextPage and not response:
                yield "DONE PAGING"
            elif response and hasNextPage:
                page_count += 1
                logger.info(f"Page: {page_count}")
                try:
                    yield response
                except ValueError as e:
                    logger.error(f"""
                    page_count: {page_count}
                    response: {response}
                    {e}
                    """)
                    raise

    def _detailed_error(self, responses, page, hasNextPage):
        if len(responses) > 4:
            responses.pop()  # control amount of RAM consumed
        previous = responses[len(responses) - 1]
        pretty_previous = helpers.pretty_string_dict(previous[0], with_empties=False)
        logger.error(f"""
        Paged #{page} pages
        Current hasNextPage value: {hasNextPage}
        Previous response:
        """ + pretty_previous)