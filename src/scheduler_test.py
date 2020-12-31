from parameterized import parameterized
from unittest import mock
import unittest

import scheduler


def _gen_user(name):
  return mock.MagicMock(name=str(name), id=name, nick=str(name), uuid=name)


class SchedulerTestCase(unittest.TestCase):
  @parameterized.expand([
    ('single list', ['test_user'], 'test_user'),
    ('multiple users', ['first', 'second', 'third'], 'first')
  ])
  def test_on_call(self, name, users, on_call_user):
    sch = scheduler.Scheduler(users)
    self.assertEqual(sch.on_call, on_call_user)

  @mock.patch('pytablewriter.MarkdownTableWriter')
  def test_schedule_gen_simple(self, mock_writer):
    users = [_gen_user(i) for i in range(1, 5)]

    sch = scheduler.Scheduler(users)
    sch.generate_schedule()

    _, kwargs = mock_writer.call_args
    self.assertListEqual(kwargs['value_matrix'], 
                         [['1', '2', '3', '4', '1', '2', '3']])

  @mock.patch('pytablewriter.MarkdownTableWriter')
  def test_schedule_gen_not_signed_off(self, mock_writer):
    users = [_gen_user(i) for i in range(1, 5)]

    sch = scheduler.Scheduler(users)

    sch.signed_off = False
    self.assertFalse(sch.signed_off)
    
    sch.generate_schedule()

    _, kwargs = mock_writer.call_args
    self.assertIn('today', kwargs['headers'][0])

  @mock.patch('pytablewriter.MarkdownTableWriter')
  def test_schedule_gen_signed_off(self, mock_writer):
    users = [_gen_user(i) for i in range(1, 5)]

    sch = scheduler.Scheduler(users)

    sch.signed_off = True
    self.assertTrue(sch.signed_off)
    
    sch.generate_schedule()

    _, kwargs = mock_writer.call_args
    self.assertIn('tmrw', kwargs['headers'][0])

  @parameterized.expand([
    ('size 2', [0, 1], 0, 1, [1, 0]),
    ('size 5', [0, 1, 2, 3, 4], 1, 4, [0, 4, 2, 3, 1]),
  ])
  def test_swap_happy(self, name, before_users, idx1, idx2, after_users):
    pre_users = [_gen_user(u) for u in before_users]
    sch = scheduler.Scheduler(pre_users)
    self.assertListEqual(sch._users, pre_users)

    val1 = pre_users[idx1]
    val2 = pre_users[idx2]
    sch.swap(val1, val2)

    self.assertListEqual([u.uuid for u in sch._users],
                         after_users)

  def test_swap_same_person(self):
    user = _gen_user('test_user')
    sch = scheduler.Scheduler([user])

    with self.assertRaises(ValueError):
      sch.swap(user, user)

if __name__ == '__main__':
  unittest.main()