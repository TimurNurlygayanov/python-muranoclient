# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

import routes

from windc.api.v1 import datacenters
from windc.api.v1 import services
from openstack.common import wsgi


LOG = logging.getLogger(__name__)


class API(wsgi.Router):

    """WSGI router for windc v1 API requests."""

    def __init__(self, conf, **local_conf):
        self.conf = conf
        mapper = routes.Mapper()
        tenant_mapper = mapper.submapper(path_prefix="/{tenant_id}")
        datacenter_resource = datacenters.create_resource(self.conf)
        datacenter_collection = tenant_mapper.collection(
			"datacenters", "datacenter",
			controller=datacenter_resource,
                        member_prefix="/{datacenter_id}",
			formatted=False)
        service_resource = services.create_resource(self.conf)
        service_collection = datacenter_collection.member.\
                             collection('services','service',
                                        controller=service_resource,
                                        member_prefix="/{service_id}",
                                        formatted=False)
        service_collection.member.connect("/{status}",
                                          action="changeServiceStatus",
                                          conditions={'method': ["PUT"]})
        mapper.connect("/servicetypes",
                       controller=datacenter_resource,
                       action="show_servicetypes",
                       conditions={'method': ["GET"]})
        super(API, self).__init__(mapper)