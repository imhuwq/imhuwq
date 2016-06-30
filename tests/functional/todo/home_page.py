from ..base import FunctionalTest

import re


class HomePageGeneralTest(FunctionalTest):
    def test_01_home_page_is_accessable(self):
        """测试首页可以正常访问"""

        # 打开首页
        self.client.get(self.host + '/todo')
        expected_title = 'ToDo - %s' % self.app.config['SITE_TITLE']
        real_title = self.client.title
        self.assertEqual(expected_title, real_title)

    def test_02_home_page_components(self):
        """测试首页主要元素"""
        self.client.get(self.host + '/todo')

        # 存在导航栏 nav
        navbar = self.find_or_None(self.client.find_element_by_css_selector)('.navbar-fixed-top')
        self.assertTrue(navbar is not None, msg="顶部导航栏不存在")

        # 存在添加任务输入框 input
        input_task = self.find_or_None(self.client.find_element_by_id)('id-task-input')
        self.assertTrue(input_task is not None, msg="任务输入框不存在")

        # 存在任务列表 ul
        task_list = self.find_or_None(self.client.find_element_by_id)('id-task-list')
        self.assertTrue(task_list is not None, msg="任务列表不存在")

        # 侧边栏存在近期统计和预告 div
        info_panel = self.find_or_None(self.client.find_element_by_id)('id-info-panel')
        self.assertTrue(info_panel is not None, msg="信息栏不存在")

        # 侧边栏可以创建项目 project
        create_project = self.find_or_None(self.client.find_element_by_id)('id-create-project')
        self.assertTrue(info_panel is not None, msg="创建项目栏不存在")

        # 存在footer
        footer = self.find_or_None(self.client.find_element_by_css_selector)('.page-footer')
        self.assertTrue(info_panel is not None, msg="footer不存在")


class TaskListTest(FunctionalTest):
    def test_01_task_list_style(self):
        """测试任务列表"""

        self.client.get(self.host + '/todo')
        # 各类型任务颜色不同
        task_11 = self.find_or_None(self.client.find_element_by_css_selector)('.cls-task-11')
        self.assertTrue(re.search('list-group-item-danger', task_11.get_attribute('class')))

        task_10 = self.find_or_None(self.client.find_element_by_css_selector)('.cls-task-10')
        self.assertTrue(re.search('list-group-item-info', task_10.get_attribute('class')))

        task_01 = self.find_or_None(self.client.find_element_by_css_selector)('.cls-task-01')
        self.assertTrue(re.search('list-group-item-warning', task_01.get_attribute('class')))

        task_00 = self.find_or_None(self.client.find_element_by_css_selector)('.cls-task-00')
        self.assertTrue(re.search('list-group-item-text', task_00.get_attribute('class')))

        # 任务列表左边是序号，其次是期限，再次是内容，最后是打钩
        task_order = self.find_or_None(task_11.find_element_by_css_selector)('.cls-task-order')
        self.assertTrue(task_order is not None)
        task_dl = self.find_or_None(task_11.find_element_by_css_selector)('.cls-task-dl')
        self.assertTrue(task_dl is not None)
        task_done = self.find_or_None(task_11.find_element_by_css_selector)('.cls-task-done')
        self.assertTrue(task_done is not None)

    def test_02_task_list_action(self):
        """测试任务列表操作"""

        self.client.get(self.host + '/todo')

        # 输入框快速添加任务
        input_task = self.find_or_None(self.client.find_element_by_id)('id-task-input')
        input_task.send_keys('@11 完成测试\n')

        task_11 = self.find_or_None(self.client.find_elements_by_css_selector)('.cls-task-11')[0]
        self.assertTrue(re.search('完成测试', task_11.text))
        self.assertTrue(re.search('list-group-item-danger', task_11.get_attribute('class')))

        # 双击任务完成

        # 右击任务完修改
