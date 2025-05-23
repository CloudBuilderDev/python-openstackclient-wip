# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock


from openstack.block_storage.v3 import group_type
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_group_type
from openstackclient.volume.v3.volume_group_type import _format_group_type


class TestVolumeGroupTypeCreate(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.fake_volume_group_type = sdk_fakes.generate_fake_resource(
            group_type.GroupType,
            id='fake_id',
            name='fake_name',
            description='fake_desc',
            is_public=True,
            group_specs={'k1': 'v1'},
            volume_types=['gold', 'silver'],
        )
        self.expected_columns, self.expected_data = (
            volume_group_type._format_group_type(self.fake_volume_group_type)
        )

        self.app.client_manager.sdk_connection = self.volume_sdk_client
        self.volume_sdk_client.block_storage = mock.Mock()

        self.mv_patcher = mock.patch(
            'openstackclient.volume.v3.volume_group_type.sdk_utils.supports_microversion',
            return_value=True,
        )
        self.mock_support = self.mv_patcher.start()
        self.addCleanup(self.mv_patcher.stop)

        self.volume_sdk_client.block_storage.create_group_type.return_value = (
            self.fake_volume_group_type
        )

        self.cmd = volume_group_type.CreateVolumeGroupType(self.app, None)

    def test_volume_group_type_create(self):
        self.set_volume_api_version('3.11')

        arglist = [
            self.fake_volume_group_type.name,
        ]
        verifylist = [
            ('name', self.fake_volume_group_type.name),
            ('description', None),
            ('is_public', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.block_storage.create_group_type.assert_called_once_with(
            name=self.fake_volume_group_type.name,
            description=None,
            is_public=True,
        )

        self.assertEqual(self.expected_columns, columns)
        self.assertCountEqual(self.expected_data, data)

    def test_volume_group_type_create_with_options(self):
        self.set_volume_api_version('3.11')

        arglist = [
            self.fake_volume_group_type.name,
            '--description',
            'foo',
            '--private',
        ]
        verifylist = [
            ('name', self.fake_volume_group_type.name),
            ('description', 'foo'),
            ('is_public', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.block_storage.create_group_type.assert_called_once_with(
            name=self.fake_volume_group_type.name,
            description='foo',
            is_public=False,
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertCountEqual(self.expected_data, data)

    def test_volume_group_type_create_pre_v311(self):
        self.set_volume_api_version('3.10')
        self.mock_support.return_value = False

        arglist = [
            self.fake_volume_group_type.name,
        ]
        verifylist = [
            ('name', self.fake_volume_group_type.name),
            ('description', None),
            ('is_public', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeDelete(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()
        self.fake_volume_group_type = sdk_fakes.generate_fake_resource(
            group_type.GroupType,
            id='gid-1',
            name='gname',
            description='desc',
            is_public=True,
            group_specs={'k': 'v'},
            volume_types=['gold', 'silver'],
        )

        self.app.client_manager.sdk_connection = self.volume_sdk_client
        self.volume_sdk_client.block_storage = mock.Mock()

        self.mv_patcher = mock.patch(
            'openstackclient.volume.v3.volume_group_type.sdk_utils.supports_microversion',
            return_value=True,
        )
        self.mock_support = self.mv_patcher.start()
        self.addCleanup(self.mv_patcher.stop)

        self.volume_sdk_client.block_storage.find_group_type.return_value = (
            self.fake_volume_group_type
        )

        self.cmd = volume_group_type.DeleteVolumeGroupType(self.app, None)

    def test_volume_group_type_delete(self):
        arglist = [
            self.fake_volume_group_type.id,
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.block_storage.find_group_type.assert_called_once_with(
            self.fake_volume_group_type.id,
            ignore_missing=False,
        )
        self.volume_sdk_client.block_storage.delete_group_type.assert_called_once_with(
            self.fake_volume_group_type,
        )

        self.assertIsNone(result)

    def test_volume_group_type_delete_pre_v311(self):
        self.set_volume_api_version('3.10')
        self.mock_support.return_value = False

        arglist = [
            self.fake_volume_group_type.id,
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeSet(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()
        self.fake_volume_group_type = sdk_fakes.generate_fake_resource(
            group_type.GroupType,
            id='fake_id',
            name='fake_name',
            description='fake_desc',
            is_public=True,
            group_specs={'k1': 'v1'},
            volume_types=['gold', 'silver'],
        )
        self.expected_columns, self.expected_data = (
            volume_group_type._format_group_type(self.fake_volume_group_type)
        )

        self.app.client_manager.sdk_connection = self.volume_sdk_client
        self.volume_sdk_client.block_storage = mock.Mock()

        self.mv_patcher = mock.patch(
            'openstackclient.volume.v3.volume_group_type.sdk_utils.supports_microversion',
            return_value=True,
        )
        self.mock_support = self.mv_patcher.start()
        self.addCleanup(self.mv_patcher.stop)

        self.volume_sdk_client.block_storage.find_group_type.return_value = (
            self.fake_volume_group_type
        )
        self.volume_sdk_client.block_storage.update_group_type.return_value = (
            self.fake_volume_group_type
        )
        self.volume_sdk_client.block_storage.set_group_type_specs.return_value = None

        self.cmd = volume_group_type.SetVolumeGroupType(self.app, None)

    def test_volume_group_type_set(self):
        self.set_volume_api_version('3.11')
        self.volume_sdk_client.block_storage.set_group_type_specs.return_value = None

        arglist = [
            self.fake_volume_group_type.id,
            '--name',
            'foo',
            '--description',
            'hello, world',
            '--public',
            '--property',
            'fizz=buzz',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('name', 'foo'),
            ('description', 'hello, world'),
            ('is_public', True),
            ('no_property', False),
            ('properties', {'fizz': 'buzz'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.block_storage.update_group_type.assert_called_once_with(
            self.fake_volume_group_type,
            name='foo',
            description='hello, world',
            is_public=True,
        )
        self.volume_sdk_client.block_storage.set_group_type_specs.assert_called_once_with(
            self.fake_volume_group_type,
            {'fizz': 'buzz'},
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_volume_group_type_with_no_property_option(self):
        self.set_volume_api_version('3.11')
        self.volume_sdk_client.block_storage.get_group_type_specs.return_value = {
            'foo': 'bar'
        }
        self.volume_sdk_client.block_storage.unset_group_type_specs.return_value = None
        self.volume_sdk_client.block_storage.set_group_type_specs.return_value = None

        arglist = [
            self.fake_volume_group_type.id,
            '--no-property',
            '--property',
            'fizz=buzz',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('name', None),
            ('description', None),
            ('is_public', None),
            ('no_property', True),
            ('properties', {'fizz': 'buzz'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.block_storage.get_group_type_specs.assert_called_once_with(
            self.fake_volume_group_type
        )
        self.volume_sdk_client.block_storage.unset_group_type_specs.assert_called_once_with(
            self.fake_volume_group_type, ['foo']
        )
        self.volume_sdk_client.block_storage.set_group_type_specs.assert_called_once_with(
            self.fake_volume_group_type, {'fizz': 'buzz'}
        )

        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_volume_group_type_set_pre_v311(self):
        self.set_volume_api_version('3.10')
        self.mock_support.return_value = False

        arglist = [
            self.fake_volume_group_type.id,
            '--name',
            'foo',
            '--description',
            'hello, world',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('name', 'foo'),
            ('description', 'hello, world'),
            ('is_public', None),
            ('no_property', False),
            ('properties', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeUnset(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()
        self.fake_volume_group_type = sdk_fakes.generate_fake_resource(
            group_type.GroupType,
            id='gid-1',
            name='gname',
            description='desc',
            is_public=True,
            group_specs={'k': 'v'},
            volume_types=['gold', 'silver'],
        )
        self.expected_columns, self.expected_data = (
            volume_group_type._format_group_type(self.fake_volume_group_type)
        )

        self.app.client_manager.sdk_connection = self.volume_sdk_client
        self.volume_sdk_client.block_storage = mock.Mock()

        self.mv_patcher = mock.patch(
            'openstackclient.volume.v3.volume_group_type.sdk_utils.supports_microversion',
            return_value=True,
        )
        self.mock_support = self.mv_patcher.start()
        self.addCleanup(self.mv_patcher.stop)

        self.volume_sdk_client.block_storage.find_group_type.return_value = (
            self.fake_volume_group_type
        )
        self.volume_sdk_client.block_storage.get_group_type.return_value = (
            self.fake_volume_group_type
        )
        self.volume_sdk_client.block_storage.unset_group_type_specs.return_value = None

        self.cmd = volume_group_type.UnsetVolumeGroupType(self.app, None)

    def test_volume_group_type_unset(self):
        self.set_volume_api_version('3.11')

        arglist = [
            self.fake_volume_group_type.id,
            '--property',
            'fizz',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('properties', ['fizz']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.block_storage.find_group_type.assert_called_once_with(
            self.fake_volume_group_type.id,
            ignore_missing=False,
        )
        self.volume_sdk_client.block_storage.unset_group_type_specs.assert_called_once_with(
            self.fake_volume_group_type,
            ['fizz'],
        )
        self.volume_sdk_client.block_storage.get_group_type.assert_called_once_with(
            self.fake_volume_group_type.id,
        )

        self.assertEqual(self.expected_columns, columns)
        self.assertCountEqual(self.expected_data, data)

    def test_volume_group_type_unset_pre_v311(self):
        self.set_volume_api_version('3.10')
        self.mock_support.return_value = False

        arglist = [
            self.fake_volume_group_type.id,
            '--property',
            'fizz',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('properties', ['fizz']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeList(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()
        self.fake_volume_group_types = [
            sdk_fakes.generate_fake_resource(
                group_type.GroupType,
                id=f'gid-{i}',
                name=f'gname-{i}',
                description='desc',
                is_public=bool(i % 2),
                group_specs={'k': f'v{i}'},
            )
            for i in range(2)
        ]

        self.mv_patcher = mock.patch(
            'openstackclient.volume.v3.volume_group_type.sdk_utils.supports_microversion',
            return_value=True,
        )
        self.mock_support = self.mv_patcher.start()
        self.addCleanup(self.mv_patcher.stop)

        self.app.client_manager.sdk_connection = self.volume_sdk_client
        self.volume_sdk_client.block_storage = mock.Mock()

        self.volume_sdk_client.block_storage.group_types.return_value = (
            self.fake_volume_group_types
        )
        self.volume_sdk_client.block_storage.get_default_group_type.return_value = self.fake_volume_group_types[
            0
        ]

        self.cmd = volume_group_type.ListVolumeGroupType(self.app, None)
        self.expected_columns = ('ID', 'Name', 'Is Public', 'Properties')
        self.expected_data = [
            (
                fake_volume_group_type.id,
                fake_volume_group_type.name,
                fake_volume_group_type.is_public,
                fake_volume_group_type.group_specs,
            )
            for fake_volume_group_type in self.fake_volume_group_types
        ]

    def test_volume_group_type_list(self):
        self.set_volume_api_version('3.11')

        arglist = []
        verifylist = [
            ('show_default', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.block_storage.group_types.assert_called_once_with()
        self.assertEqual(self.expected_columns, columns)
        self.assertCountEqual(tuple(self.expected_data), data)

    def test_volume_group_type_list_with_default_option(self):
        self.set_volume_api_version('3.11')

        arglist = [
            '--default',
        ]
        verifylist = [
            ('show_default', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.block_storage.get_default_group_type.assert_called_once_with()
        self.assertEqual(self.expected_columns, columns)
        self.assertCountEqual(tuple([self.expected_data[0]]), data)

    def test_volume_group_type_list_pre_v311(self):
        self.set_volume_api_version('3.10')
        self.mock_support.return_value = False

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeShow(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.fake_volume_group_type = sdk_fakes.generate_fake_resource(
            group_type.GroupType,
            id="gt-123",
            name="gold",
            description=None,
            is_public=True,
            group_specs={"tier": "gold"},
        )
        self.expected_columns, self.expected_data = _format_group_type(
            self.fake_volume_group_type
        )

        self.conn = mock.Mock()
        self.conn.block_storage.find_group_type.return_value = (
            self.fake_volume_group_type
        )
        self.app.client_manager.sdk_connection = self.conn

        p = mock.patch('openstack.utils.supports_microversion', autospec=True)
        self.addCleanup(p.stop)
        self.mock_supports = p.start()

        self.cmd = volume_group_type.ShowVolumeGroupType(self.app, None)

    def test_volume_group_type_show(self):
        self.set_volume_api_version('3.11')
        self.mock_supports.return_value = True

        arglist = [self.fake_volume_group_type.id]
        verifylist = [('group_type', self.fake_volume_group_type.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.conn.block_storage.find_group_type.assert_called_once_with(
            self.fake_volume_group_type.id,
            ignore_missing=False,
        )

        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_volume_group_type_show_pre_v311(self):
        self.set_volume_api_version('3.10')
        self.mock_supports.return_value = False

        arglist = [self.fake_volume_group_type.id]
        verifylist = [('group_type', self.fake_volume_group_type.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )
