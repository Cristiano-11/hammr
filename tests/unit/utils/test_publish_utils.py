# Copyright (c) 2007-2018 UShareSoft, All rights reserved
#
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
from unittest import TestCase

from hammr.utils.publish_utils import *
from hammr.utils.hammr_utils import *
from uforge.application import Api
from uforge.objects.uforge import *
from uforge.objects import uforge
from tests.unit.utils.file_utils import findRelativePathFor
from mock import patch
import hammr.commands.image

class TestPublishUtils(TestCase):

    app_uri = 'users/guest/appliances/5/images/1234/'
    scan_uri = 'users/guest/scannedinstances/5/scans/12/images/1234'
    published_app_uri = 'users/guest/appliances/5/images/1234/pimages/5678'
    published_scan_uri = 'users/guest/scannedinstances/5/scans/12/images/1234/pimages/5678'

    def test_is_image_ready_to_publish_returns_true_when_memory_and_swap_size_are_defined(self):
        # given
        image = self.build_image_to_publish("complete", True, self.app_uri)
        file = findRelativePathFor("tests/integration/data/publish_builder.yml")
        builder = self.build_builder(file)

        # when
        image_ready = is_image_ready_to_publish(image, builder)

        # then
        self.assertEqual(image_ready, True)

    def test_is_image_ready_to_publish_returns_false_when_status_is_cancelled(self):
        # given
        image = self.build_image_to_publish("cancelled", False, self.app_uri)
        file = findRelativePathFor("tests/integration/data/publish_builder.yml")
        builder = self.build_builder(file)

        # when
        image_ready = is_image_ready_to_publish(image, builder)

        # then
        self.assertEqual(image_ready, False)

    @patch('uforge.application.Api._Users._Scannedinstances._Scans._Images._Pimages.Publish')
    def test_call_publish_webservice_returns_published_image_for_a_scan_image(self, mock_scan_publish):
        #given
        mock_scan_publish.return_value = self.build_published_image(self.published_scan_uri)
        image = self.build_image_to_publish("complete", True, self.scan_uri)
        image_object = self.build_image_object()
        source =self.build_source_scan()

        #when
        published_image = call_publish_webservice(image_object, image, source, None)

        #then
        self.assertEqual(type(published_image), type(PublishImageAws()))

    @patch('uforge.application.Api._Users._Appliances._Images._Pimages.Publish')
    def test_call_publish_webservice_returns_published_image_for_a_template_image(self, mock_template_publish):
        #given
        mock_template_publish.return_value = self.build_published_image(self.published_app_uri)
        image = self.build_image_to_publish("complete", True, self.app_uri)
        image_object = self.build_image_object()
        source =self.build_source_template()

        #when
        published_image = call_publish_webservice(image_object, image, source, None)

        #then
        self.assertEqual(type(published_image), type(PublishImageAws()))

    def test_call_publish_webservice_raises_exception_for_wrong_image_uri(self):
        #given
        image = self.build_image_to_publish("complete", True, 'wrong/uri/')
        image_object = self.build_image_object()
        source =self.build_source_template()

        #when
        try :
            call_publish_webservice(image_object, image, source, None)

        #then
            self.assertTrue(False)
        except :
            self.assertTrue(True)

    def build_builder(self, file):
        builder = retrieve_template_from_file(file)
        return builder

    def build_image_to_publish(self, status, status_complete, uri):
        image = Image()
        image.dbId = 1234
        image.uri = uri
        image.status = status
        image.status.complete = status_complete

        install_profile = InstallProfile()
        install_profile.memorySize = 1024
        install_profile.swapSize = 1024

        image.installProfile = install_profile
        return image

    def build_source_scan(self):
        source = Scan()
        source.uri = self.scan_uri
        return source

    def build_source_template(self):
        source = Appliance()
        source.uri = self.app_uri
        return source

    def build_published_image(self, uri):
        image = PublishImageAws()
        image.dbId = 5678
        image.imageUri = uri
        return image

    def build_image_object(self):
        image_object = hammr.commands.image.Image()
        api = Api(None, username="user", password="pass", headers=None,
                  disable_ssl_certificate_validation=True, timeout=constants.HTTP_TIMEOUT)
        image_object.api = api
        image_object.login = "guest"
        return image_object

class TestPublishAzure(TestCase):

    def test_publish_azure_should_return_publish_image_when_valid_entries_withResourceGroup(self):
        # given
        builder = self.build_azure_builder("myStorageAccount", "myContainer", "myBlob", "myDisplayName", "myResourceGroup")

        # when
        pimage = publish_azure(builder)

        # then
        self.assertNotEqual(pimage, None)
        self.assertEqual(pimage.storageAccount, builder["storageAccount"])
        self.assertEqual(pimage.container, builder["container"])
        self.assertEqual(pimage.blob, builder["blob"])
        self.assertEqual(pimage.displayName, builder["displayName"])
        self.assertEqual(pimage.resourceGroup, builder["resourceGroup"])

    def test_publish_azure_should_return_publish_image_when_valid_entries_withoutResourceGroup(self):
        # given
        builder = self.build_azure_builder("myStorageAccount", "myContainer", "myBlob", "myDisplayName", None)

        # when
        pimage = publish_azure(builder)

        # then
        self.assertNotEqual(pimage, None)
        self.assertEqual(pimage.storageAccount, builder["storageAccount"])
        self.assertEqual(pimage.container, builder["container"])
        self.assertEqual(pimage.blob, builder["blob"])
        self.assertEqual(pimage.displayName, builder["displayName"])
        self.assertEqual(pimage.resourceGroup, None)

    def test_publish_azure_should_return_none_when_missing_container(self):
        # given
        builder = self.build_azure_builder("myStorageAccount", None, "myBlob", "myDisplayName", "myResourceGroup")

        # when
        pimage = publish_azure(builder)

        # then
        self.assertEqual(pimage, None)

    def test_publish_azure_should_return_none_when_missing_blob(self):
        # given
        builder = self.build_azure_builder("myStorageAccount", "myContainer", None, "myDisplayName", "myResourceGroup")

        # when
        pimage = publish_azure(builder)

        # then
        self.assertEqual(pimage, None)

    def test_publish_azure_should_return_none_when_missing_displayName(self):
        # given
        builder = self.build_azure_builder("myStorageAccount", "myContainer", "myBlob", None, "myResourceGroup")

        # when
        pimage = publish_azure(builder)

        # then
        self.assertEqual(pimage, None)

    def build_azure_builder(self, storageAccount, container, blob, displayName, resourceGroup):
        builder = {}
        if storageAccount is not None: builder["storageAccount"] = storageAccount
        if container is not None: builder["container"] = container
        if blob is not None: builder["blob"] = blob
        if displayName is not None: builder["displayName"] = displayName
        if resourceGroup is not None: builder["resourceGroup"] = resourceGroup
        return builder

class TestPublishCloudStack(TestCase):

    def test_publish_cloudstack_should_return_publish_image_when_valid_entries(self):
        # given
        builder = self.build_cloudstack_builder("myImageName", "myZone", "myDescription")

        # when
        pimage = publish_cloudstack(builder)

        # then
        self.assertNotEqual(pimage, None)
        self.assertEqual(pimage.displayName, builder["imageName"])
        self.assertEqual(pimage.zoneName, builder["zone"])
        self.assertEqual(pimage.description, builder["description"])

    def test_publish_cloudstack_should_return_none_when_missing_image_name(self):
        # given
        builder = self.build_cloudstack_builder(None, "myZone", "myDescription")

        # when
        pimage = publish_cloudstack(builder)

        # then
        self.assertEqual(pimage, None)

    def test_publish_cloudstack_should_return_none_when_missing_zone(self):
        # given
        builder = self.build_cloudstack_builder("myImageName", None, "myDescription")

        # when
        pimage = publish_cloudstack(builder)

        # then
        self.assertEqual(pimage, None)

    def test_publish_cloudstack_should_return_none_when_missing_description(self):
        # give
        builder = self.build_cloudstack_builder("myImageName", "myZone", None)

        # when
        pimage = publish_cloudstack(builder)

        # then
        self.assertEqual(pimage, None)


    def build_cloudstack_builder(self, image_name, zone, description):
        builder = {}
        if image_name is not None: builder["imageName"] = image_name
        if zone is not None: builder["zone"] = zone
        if description is not None: builder["description"] = description
        return builder

class TestPublishOracle(TestCase):
    def test_publish_oracle_should_return_publish_image_when_valid_entries(self):
        # given
        builder = self.build_builder("displayName", "computeEndPoint")

        # when
        pimage = publish_oracleraw(builder)

        # then
        self.assertEqual(pimage.displayName, builder["displayName"])
        self.assertEqual(pimage.computeEndPoint, builder["computeEndPoint"])

    def test_publish_oracle_should_return_none_when_missing_display_name(self):
        # given
        builder = self.build_builder(None, "computeEndPoint")

        # when
        pimage = publish_oracleraw(builder)

        # then
        self.assertEqual(pimage, None)

    def test_publish_oracle_should_return_none_when_missing_compute_end_point(self):
        # given
        builder = self.build_builder("displayName", None)

        # when
        pimage = publish_oracleraw(builder)

        # then
        self.assertEqual(pimage, None)

    def build_builder(self, display_name, compute_end_point):
        builder = {}
        if display_name is not None: builder["displayName"] = display_name
        if compute_end_point is not None: builder["computeEndPoint"] = compute_end_point
        return builder


class TestPublishOutscale(TestCase):
    def test_publish_outscale_should_return_publish_image_when_valid_entries(self):
        # given
        builder = self.build_outscale_builder("myRegion")

        # when
        pimage = publish_outscale(builder)

        # then
        self.assertNotEqual(pimage, None)
        self.assertNotEqual(pimage.region, None)
        self.assertEqual(pimage.region, builder["region"])

    def test_publish_outscale_should_return_none_when_missing_region(self):
        # given
        builder = self.build_outscale_builder(None)

        # when
        pimage = publish_outscale(builder)

        # then
        self.assertEqual(pimage, None)

    def build_outscale_builder(self, region):
        builder = {}
        if region is not None:
            builder["region"] = region
        return builder