from parameterized import parameterized

import scheduler
import unittest


class SchedulerTestCase(unittest.TestCase):
  @parameterized.expand([
    ('single list', ['test_user'], 'test_user'),
    ('multiple users', ['first', 'second', 'third'], 'first')
  ])
  def test_on_call(self, name, users, on_call_user):
    sch = scheduler.Scheduler(users)
    self.assertEqual(sch.on_call, on_call_user)


if __name__ == '__main__':
  unittest.main()