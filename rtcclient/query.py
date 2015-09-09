from rtcclient.base import RTCBase
import logging
from rtcclient import urlquote
from rtcclient.models import SavedQuery


class Query(RTCBase):
    """A wrapped class to perform all query-related actions

    :param rtc_obj: a reference to the
        :class:`rtcclient.client.RTCClient` object
    """

    log = logging.getLogger("query:Query")

    def __init__(self, rtc_obj):
        """Initialize <Query> object"""

        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, self.rtc_obj.url)

    def __str__(self):
        return "Query @ %s" % self.rtc_obj

    def get_rtc_obj(self):
        return self.rtc_obj

    def queryWorkitems(self, query_str, projectarea_id=None,
                       projectarea_name=None, returned_properties=None,
                       archived=False):
        """Query workitems with the query string in a certain
        :class:`rtcclient.project_area.ProjectArea`

        At least either of `projectarea_id` and `projectarea_name` is given

        :param query_str: a valid query string
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the
            :class:`rtcclient.project_area.ProjectArea` name
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :param archived (default is False): whether the
            :class:`rtcclient.workitem.Workitem` is archived
        :return: a :class:`list` that contains the queried
            :class:`rtcclient.workitem.Workitem` objects
        :rtype: list
        """

        pa_id = (self.rtc_obj
                     ._pre_get_resource(projectarea_id=projectarea_id,
                                        projectarea_name=projectarea_name))

        self.log.info("Start to query workitems with query string: %s",
                      query_str)
        query_str = urlquote(query_str)
        rp = returned_properties

        return (self.rtc_obj
                    ._get_paged_resources("Query",
                                          projectarea_id=pa_id,
                                          customized_attr=query_str,
                                          page_size="100",
                                          returned_properties=rp,
                                          archived=archived))

    def getAllSavedQueries(self, projectarea_id=None, projectarea_name=None,
                           creator=None, saved_query_name=None):
        """Get all saved queries created by somebody (optional)
        in a certain project area (optional, either `projectarea_id`
        or `projectarea_name` is needed if specified)

        If `saved_query_name` is specified, only the saved queries match the
        name will be fetched.

        Note: only if `creator` is added as a member, the saved queries
        can be found. Otherwise None will be returned.

        WARNING: now the RTC server cannot correctly list all the saved queries
        It seems to be a bug of RTC. Recommend using `runSavedQueryByUrl` to
        query all the workitems if the query is saved.

        Note: It will run faster when more attributes are specified.

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the
            :class:`rtcclient.project_area.ProjectArea` name
        :param creator: the creator email address
        :param saved_query_name: the saved query name
        :return: a :class:`list` that contains the saved queried
            :class:`rtcclient.models.SavedQuery` objects
        :rtype: list
        """

        pa_id = (self.rtc_obj
                     ._pre_get_resource(projectarea_id=projectarea_id,
                                        projectarea_name=projectarea_name))

        filter_rule = None
        if creator is not None:
            fcreator = self.rtc_obj.getOwnedBy(creator).url
            filter_rule = [("dc:creator", "@rdf:resource",
                            fcreator)]

        if saved_query_name is not None:
            ftitle_rule = ("dc:title", None, saved_query_name)
            if filter_rule is None:
                filter_rule = [ftitle_rule]
            else:
                filter_rule.append(ftitle_rule)

        return (self.rtc_obj
                    ._get_paged_resources("SavedQuery",
                                          projectarea_id=pa_id,
                                          page_size="100",
                                          filter_rule=filter_rule))

    def getSavedQueriesByName(self, saved_query_name, projectarea_id=None,
                              projectarea_name=None, creator=None):
        """Get all saved queries match the name created by somebody (optional)
        in a certain project area (optional, either `projectarea_id`
        or `projectarea_name` is needed if specified)

        Note: only if `creator` is added as a member, the saved queries
        can be found. Otherwise None will be returned.

        WARNING: now the RTC server cannot correctly list all the saved queries
        It seems to be a bug of RTC. Recommend using `runSavedQueryByUrl` to
        query all the workitems if the query is saved.

        :param saved_query_name: the saved query name
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the
            :class:`rtcclient.project_area.ProjectArea` name
        :param creator: the creator email address
        :return: a :class:`list` that contains the saved queried
            :class:`rtcclient.models.SavedQuery` objects
        :rtype: list
        """

        return self.getAllSavedQueries(projectarea_id=projectarea_id,
                                       projectarea_name=projectarea_name,
                                       creator=creator,
                                       saved_query_name=saved_query_name)

    def getMySavedQueries(self, projectarea_id=None, projectarea_name=None,
                          saved_query_name=None):
        """Get all saved queries created by me in a certain project
        area (optional, either `projectarea_id` or `projectarea_name` is
        needed if specified)

        Note: only if myself is added as a member, the saved queries
        can be found. Otherwise None will be returned.

        WARNING: now the RTC server cannot correctly list all the saved queries
        It seems to be a bug of RTC. Recommend using `runSavedQueryByUrl` to
        query all the workitems if the query is saved.

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the
            :class:`rtcclient.project_area.ProjectArea` name
        :param saved_query_name: the saved query name
        :return: a :class:`list` that contains the saved queried
            :class:`rtcclient.models.SavedQuery` objects
        :rtype: list
        """

        return self.getAllSavedQueries(projectarea_id=projectarea_id,
                                       projectarea_name=projectarea_name,
                                       creator=self.rtc_obj.username,
                                       saved_query_name=saved_query_name)

    def runSavedQueryByUrl(self, saved_query_url, returned_properties=None):
        """Query workitems using the saved query url

        :param saved_query_url: the saved query url
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: a :class:`list` that contains the queried
            :class:`rtcclient.workitem.Workitem` objects
        :rtype: list
        """

        saved_query_id = saved_query_url.split("=")[-1]
        return self._runSavedQuery(saved_query_id,
                                   returned_properties=returned_properties)

    def runSavedQuery(self, saved_query_obj, returned_properties=None):
        """Query workitems using the :class:`rtcclient.models.SavedQuery`
        object

        :param saved_query_obj: the :class:`rtcclient.models.SavedQuery`
            object
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: a :class:`list` that contains the queried
            :class:`rtcclient.workitem.Workitem` objects
        :rtype: list
        """

        saved_query_id = saved_query_obj.results.split("/")[-2]
        return self._runSavedQuery(saved_query_id,
                                   returned_properties=returned_properties)

    def _runSavedQuery(self, saved_query_id, returned_properties=None):
        rp = returned_properties
        return (self.rtc_obj
                    ._get_paged_resources("RunQuery",
                                          page_size="100",
                                          customized_attr=saved_query_id,
                                          returned_properties=rp))
