from django.urls import reverse
from rest_framework import status

from kobo.apps.kobo_auth.shortcuts import User
from kpi.models.asset import Asset
from kpi.models.asset_file import AssetFile
from kpi.tests.base_test_case import BaseAssetTestCase
from kpi.urls.router_api_v2 import URL_NAMESPACE as ROUTER_URL_NAMESPACE


class AssetFileApiTests(BaseAssetTestCase):
    fixtures = ['test_data']
    URL_NAMESPACE = ROUTER_URL_NAMESPACE

    def setUp(self):
        self.client.login(username='someuser', password='someuser')
        self.someuser = User.objects.get(username='someuser')
        self.asset = Asset.objects.create(
            content={},
            owner=self.someuser,
            asset_type='survey',
        )
        self.url = reverse(
            self._get_endpoint('asset-file-list'),
            kwargs={'uid_asset': self.asset.uid},
        )

    @staticmethod
    def _csv_payload(filename):
        return {
            'file_type': AssetFile.FORM_MEDIA,
            'description': 'default',
            'base64Encoded': 'data:text/csv;base64,Y29sMQoxCg==',
            'metadata': {'filename': filename},
        }

    def test_rejects_csv_filename_with_spaces(self):
        response = self.client.post(
            self.url,
            self._csv_payload('lookup table.csv'),
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['base64Encoded'][0]) == (
            'CSV filenames cannot contain spaces. Rename the file and try again.'
        )

    def test_rejects_url_encoded_spaces_in_csv_filename(self):
        response = self.client.post(
            self.url,
            self._csv_payload('lookup%20table.csv'),
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['base64Encoded'][0]) == (
            'CSV filenames cannot contain spaces. Rename the file and try again.'
        )

    def test_accepts_csv_filename_without_spaces(self):
        response = self.client.post(
            self.url,
            self._csv_payload('lookup_table.csv'),
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
