#
# Copyright (c) 2014 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#

import mock

import fixture
import tempfile
import shutil
import os.path

from subscription_manager.model import Content
from subscription_manager.plugin.container import \
    ContainerContentUpdateActionCommand, KeyPair, ContainerCertDir, \
    ContainerUpdateReport

DUMMY_CERT_LOCATION = "dummy/certs"


class TestContainerContentUpdateActionCommand(fixture.SubManFixture):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix='subman-container-plugin-tests')
        self.src_certs_dir = os.path.join(self.temp_dir, "etc/pki/entitlement")
        os.makedirs(self.src_certs_dir)

        # This is where we'll setup for container certs:
        self.host_cert_dir = os.path.join(self.temp_dir,
            "etc/docker/certs.d/")
        os.makedirs(self.host_cert_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _create_content(self, label, cert):
        return Content("containerImage", label, label, cert=cert)

    def _mock_cert(self, base_filename):
        cert = mock.Mock()
        cert.path = os.path.join(self.temp_dir, DUMMY_CERT_LOCATION,
            "%s.pem" % base_filename)
        cert.key_path.return_value = os.path.join(self.temp_dir, DUMMY_CERT_LOCATION,
            "%s-key.pem" % base_filename)
        return cert

    def test_unique_paths_with_dupes(self):
        cert1 = self._mock_cert('5001')
        cert2 = self._mock_cert('5002')
        cert3 = self._mock_cert('5003')

        content1 = self._create_content('content1', cert1)
        content2 = self._create_content('content2', cert1)
        content3 = self._create_content('content3', cert2)

        # This content is provided by two other certs:
        content1_dupe = self._create_content('content1', cert2)
        content1_dupe2 = self._create_content('content1', cert3)

        contents = [content1, content2, content3, content1_dupe,
            content1_dupe2]
        cmd = ContainerContentUpdateActionCommand(None, ['cdn.example.org'],
            self.host_cert_dir)
        cert_paths = cmd._get_unique_paths(contents)
        self.assertEquals(3, len(cert_paths))
        self.assertTrue(KeyPair(cert1.path, cert1.key_path()) in cert_paths)
        self.assertTrue(KeyPair(cert2.path, cert2.key_path()) in cert_paths)
        self.assertTrue(KeyPair(cert3.path, cert3.key_path()) in cert_paths)

    def test_multi_directory(self):
        host1 = 'hostname.example.org'
        host2 = 'hostname2.example.org'
        host3 = 'hostname3.example.org'

        cert1 = self._mock_cert('5001')
        content1 = self._create_content('content1', cert1)

        self.assertFalse(os.path.exists(os.path.join(self.host_cert_dir, host1)))
        self.assertFalse(os.path.exists(os.path.join(self.host_cert_dir, host2)))
        self.assertFalse(os.path.exists(os.path.join(self.host_cert_dir, host3)))

        cmd = ContainerContentUpdateActionCommand(None, [host1, host2, host3],
            self.host_cert_dir)
        cmd._find_content = mock.Mock(return_value=[])
        cmd.perform()

        self.assertTrue(os.path.exists(os.path.join(self.host_cert_dir, host1)))
        self.assertTrue(os.path.exists(os.path.join(self.host_cert_dir, host2)))
        self.assertTrue(os.path.exists(os.path.join(self.host_cert_dir, host3)))


class TestKeyPair(fixture.SubManFixture):

    def test_expected_filenames(self):
        kp = KeyPair("/etc/pki/entitlement/9000.pem",
            "/etc/pki/entitlement/9000-key.pem")
        self.assertEquals("9000.cert", kp.dest_cert_filename)
        self.assertEquals("9000.key", kp.dest_key_filename)

    def test_expected_filenames_weird_extensions(self):
        kp = KeyPair("/etc/pki/entitlement/9000.crt",
            "/etc/pki/entitlement/9000-key.crt")
        self.assertEquals("9000.cert", kp.dest_cert_filename)
        self.assertEquals("9000.key", kp.dest_key_filename)

    def test_expected_filenames_weird_filenames(self):
        kp = KeyPair("/etc/pki/entitlement/9000.1.2014-a.pem",
            "/etc/pki/entitlement/9000.1.2014-a-key.pem")
        self.assertEquals("9000.1.2014-a.cert", kp.dest_cert_filename)
        self.assertEquals("9000.1.2014-a.key", kp.dest_key_filename)

    def test_equality(self):
        kp = KeyPair("/etc/pki/entitlement/9000.pem",
            "/etc/pki/entitlement/9000-key.pem")
        kp2 = KeyPair("/etc/pki/entitlement/9000.pem",
            "/etc/pki/entitlement/9000-key.pem")
        self.assertEqual(kp, kp2)

    def test_inequality(self):
        kp = KeyPair("/etc/pki/entitlement/9000.pem",
            "/etc/pki/entitlement/9000-key.pem")
        kp2 = KeyPair("/etc/pki/entitlement/9001.pem",
            "/etc/pki/entitlement/9001-key.pem")
        self.assertNotEqual(kp, kp2)
        self.assertNotEqual(kp, "somestring")

    def test_mixmatched_base_filenames(self):
        kp = KeyPair("/etc/pki/entitlement/9000.1.2014-a.pem",
            "/etc/pki/entitlement/9000.1.2014-a-key.pem")
        self.assertEquals("9000.1.2014-a.cert", kp.dest_cert_filename)
        self.assertEquals("9000.1.2014-a.key", kp.dest_key_filename)



class TestContainerCertDir(fixture.SubManFixture):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix='subman-container-plugin-tests')
        self.src_certs_dir = os.path.join(self.temp_dir, "etc/pki/entitlement")
        os.makedirs(self.src_certs_dir)

        # This is where we'll setup for container certs:
        container_dir = os.path.join(self.temp_dir,
            "etc/docker/certs.d/")
        os.makedirs(container_dir)

        # Where we expect our certs to actually land:
        self.dest_dir = os.path.join(container_dir, 'cdn.redhat.com')
        self.report = ContainerUpdateReport()
        self.container_dir = ContainerCertDir(self.report, 'cdn.redhat.com',
            host_cert_dir=container_dir)
        self.container_dir._rh_cdn_ca_exists = mock.Mock(return_value=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _touch(self, dir_path, filename):
        """
        Create an empty file in the given directory with the given filename.
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        open(os.path.join(dir_path, filename), 'a').close()

    def test_first_install(self):
        cert1 = '1234.pem'
        key1 = '1234-key.pem'
        self._touch(self.src_certs_dir, cert1)
        self._touch(self.src_certs_dir, key1)
        kp = KeyPair(os.path.join(self.src_certs_dir, cert1),
            os.path.join(self.src_certs_dir, key1))
        self.container_dir.sync([kp])
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, '1234.cert')))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, '1234.key')))
        self.assertEquals(2, len(self.report.added))

    def test_old_certs_cleaned_out(self):
        cert1 = '1234.cert'
        key1 = '1234.key'
        ca = 'myca.crt'  # This file extension should be left alone:
        self._touch(self.dest_dir, cert1)
        self._touch(self.dest_dir, key1)
        self._touch(self.dest_dir, ca)
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, '1234.cert')))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, '1234.key')))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, ca)))
        self.container_dir.sync([])
        self.assertFalse(os.path.exists(os.path.join(self.dest_dir, '1234.cert')))
        self.assertFalse(os.path.exists(os.path.join(self.dest_dir, '1234.key')))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, ca)))
        self.assertEquals(2, len(self.report.removed))

    def test_all_together_now(self):
        cert1 = '1234.pem'
        key1 = '1234-key.pem'
        cert2 = '12345.pem'
        key2 = '12345-key.pem'
        old_cert = '444.cert'
        old_key = '444.key'
        old_key2 = 'another.key'
        self._touch(self.src_certs_dir, cert1)
        self._touch(self.src_certs_dir, key1)
        self._touch(self.src_certs_dir, cert2)
        self._touch(self.src_certs_dir, key2)
        self._touch(self.dest_dir, old_cert)
        self._touch(self.dest_dir, old_key)
        self._touch(self.dest_dir, old_key2)
        kp = KeyPair(os.path.join(self.src_certs_dir, cert1),
            os.path.join(self.src_certs_dir, key1))
        kp2 = KeyPair(os.path.join(self.src_certs_dir, cert2),
            os.path.join(self.src_certs_dir, key2))
        self.container_dir.sync([kp, kp2])
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, '1234.cert')))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, '1234.key')))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, '12345.cert')))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, '12345.key')))

        self.assertFalse(os.path.exists(os.path.join(self.dest_dir, '444.cert')))
        self.assertFalse(os.path.exists(os.path.join(self.dest_dir, '444.key')))
        self.assertEquals(4, len(self.report.added))
        self.assertEquals(3, len(self.report.removed))

    def test_cdn_ca_symlink(self):
        cert1 = '1234.pem'
        key1 = '1234-key.pem'
        self._touch(self.src_certs_dir, cert1)
        self._touch(self.src_certs_dir, key1)
        kp = KeyPair(os.path.join(self.src_certs_dir, cert1),
            os.path.join(self.src_certs_dir, key1))
        self.container_dir.sync([kp])

        expected_symlink = os.path.join(self.dest_dir, 'redhat-uep.crt')
        self.assertTrue(os.path.exists(expected_symlink))
        self.assertTrue(os.path.islink(expected_symlink))
        self.assertEquals('/etc/rhsm/ca/redhat-uep.pem',
            os.path.realpath(expected_symlink))

    def test_cdn_ca_doesnt_exist_no_symlink(self):
        cert1 = '1234.pem'
        key1 = '1234-key.pem'
        self._touch(self.src_certs_dir, cert1)
        self._touch(self.src_certs_dir, key1)
        kp = KeyPair(os.path.join(self.src_certs_dir, cert1),
            os.path.join(self.src_certs_dir, key1))
        # Mock that /etc/rhsm/ca/redhat-uep.pem doesn't exist:
        self.container_dir._rh_cdn_ca_exists = mock.Mock(return_value=False)
        self.container_dir.sync([kp])

        expected_symlink = os.path.join(self.dest_dir, 'redhat-uep.crt')
        self.assertFalse(os.path.exists(expected_symlink))

    def test_cdn_ca_symlink_already_exists(self):

        cert1 = '1234.pem'
        key1 = '1234-key.pem'
        self._touch(self.src_certs_dir, cert1)
        self._touch(self.src_certs_dir, key1)
        kp = KeyPair(os.path.join(self.src_certs_dir, cert1),
            os.path.join(self.src_certs_dir, key1))
        self.container_dir.sync([kp])

        # Run it again, the symlink already exists:
        self.container_dir.sync([kp])
        expected_symlink = os.path.join(self.dest_dir, 'redhat-uep.crt')
        self.assertTrue(os.path.exists(expected_symlink))
        self.assertTrue(os.path.islink(expected_symlink))
        self.assertEquals('/etc/rhsm/ca/redhat-uep.pem',
            os.path.realpath(expected_symlink))
