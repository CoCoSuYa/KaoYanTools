import wx  # 导入wxPython库

import tools

self_path = None
self_url = None
self_data = None


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        super(MainWindow, self).__init__(parent, title=title, size=(500, 300), style=wx.DEFAULT_FRAME_STYLE)

        self.panel = wx.Panel(self)  # 创建面板，它是放置控件的容器
        self.sizer = wx.BoxSizer(wx.VERTICAL)  # 创建垂直盒子布局，将来可以将其他控件放入这个布局

        # 创建标签对象
        self.label = wx.StaticText(self.panel, label="包含笔记链接的excel文件路径")
        self.sizer.Add(self.label, 0, wx.EXPAND | wx.ALL, 5)  # 添加标签到布局，并设定布局选项

        # 创建多行文本框对象
        self.text_field = wx.TextCtrl(self.panel, size=(400, 80), style=wx.TE_MULTILINE)
        self.text_field.SetEditable(False)  # 设置文本框为不可编辑
        self.sizer.Add(self.text_field, 0, wx.EXPAND | wx.ALL, 5)  # 添加文本框到布局，并设定布局选项

        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 创建水平盒子布局，用于放置按钮

        # 创建"选择excel文件"按钮
        self.button_excel = wx.Button(self.panel, label="选择excel文件")
        self.button_sizer.Add(self.button_excel, 0, wx.ALL, 5)  # 添加按钮到按钮布局
        self.button_excel.Bind(wx.EVT_BUTTON, self.on_open_excel)  # 绑定按钮的点击事件到对应的处理函数

        # 创建"选择cookie文件"按钮
        self.button_cookie = wx.Button(self.panel, label="选择cookie文件")
        self.button_sizer.Add(self.button_cookie, 0, wx.ALL, 5)  # 添加按钮到按钮布局
        self.button_cookie.Bind(wx.EVT_BUTTON, self.on_open_cookie)  # 绑定按钮的点击事件到对应的处理函数

        # 创建"输出笔记数据"按钮
        self.button_note = wx.Button(self.panel, label="输出笔记数据")
        self.button_sizer.Add(self.button_note, 0, wx.ALL, 5)  # 添加按钮到按钮布局
        self.button_note.Bind(wx.EVT_BUTTON, self.on_output_note)  # 绑定按钮的点击事件到对应的处理函数

        # 创建"输出博主数据"按钮
        self.button_blogger = wx.Button(self.panel, label="输出博主数据")
        self.button_sizer.Add(self.button_blogger, 0, wx.ALL, 5)  # 添加按钮到按钮布局
        self.button_blogger.Bind(wx.EVT_BUTTON, self.on_output_blogger)  # 绑定按钮的点击事件到对应的处理函数

        self.sizer.Add(self.button_sizer, 0, wx.ALIGN_CENTER, 5)  # 添加按钮布局到主布局

        self.version_label = wx.StaticText(self.panel, label="Version: 4.0")
        self.sizer.AddStretchSpacer()  # 这将会添加一些空白空间，使标签显示在下方
        self.sizer.Add(self.version_label, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.panel.SetSizer(self.sizer)  # 将主布局设置为面板的布局

        self.Show(True)  # 显示窗口

    # "选择excel文件"按钮的事件处理函数
    def on_open_excel(self, event):
        with wx.FileDialog(self, "Open Excel file", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
                           wildcard="Excel files (*.xls,*.xlsx)|*.xls;*.xlsx") as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            global self_path, self_url
            self_path = fileDialog.GetPaths()  # 获取多个文件路径
            print(self_path)
            self.text_field.SetValue("\n".join(self_path))  # 将所有文件路径显示在文本框中，每个路径一行
            self_url = tools.read_excel_file(self_path)  # 读取Excel文件

    # "选择cookie文件"按钮的事件处理函数
    def on_open_cookie(self, event):
        with wx.FileDialog(self, "Open JSON file", wildcard="JSON files (*.json)|*.json") as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()  # 获取选定文件的完整路径
            print(pathname)
            tools.read_json_file(pathname)  # 读取JSON文件

    # "输出笔记数据"按钮的事件处理函数
    def on_output_note(self, event):
        # 在这里实现你的逻辑
        try:
            print("开始处理")
            watch = wx.StopWatch()
            watch.Start()

            global self_data
            print("读取链接:", self_url)
            note_ids = tools.get_note_ids_from_links(self_url)
            print("读取笔记id:", note_ids)
            self_data = tools.get_data(note_ids)
            print(self_data)
            nick_data_ids = []
            for data in self_data:
                # 取前两个元素
                if isinstance(data, list):
                    nick_data_ids.append(data[:2])
                else:
                    nick_data_ids.append(data)
            print(nick_data_ids)
            stop_time = watch.Time() / 1000
            tools.write_data_excel_file(self_path[0], self_data)
            weeks = tools.split_into_weeks(nick_data_ids)
            print(weeks)
            tools.write_date_excel_file(self_path[0], weeks)
            msg = f'链接数据处理完成，耗时：{stop_time:.1f}秒'
            wx.MessageBox(msg, '进度:', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            tools.export_report(str(e), "导出错误,请通知开发者排查")

    # "输出博主数据"按钮的事件处理函数
    def on_output_blogger(self, event):
        # 在这里实现你的逻辑
        try:
            watch = wx.StopWatch()
            watch.Start()
            global self_data
            self_data = tools.get_nicker_and_fans(self_url)
            print(self_data)
            tools.write_up_fans_excel_file(self_path[0], self_data)
            stop_time = watch.Time() / 1000
            msg = f'博主数据处理完成，耗时：{stop_time:.1f}秒'
            wx.MessageBox(msg, '进度:', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            tools.export_report(str(e), "导出错误,请通知开发者排查")


# 创建应用对象
app = wx.App(False)

# 创建主窗口对象
frame = MainWindow(None, "小红书数据抓取工具V4.0")

# 进入应用的主循环
app.MainLoop()
