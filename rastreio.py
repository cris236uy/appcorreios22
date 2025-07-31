selenium.common.exceptions.WebDriverException: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/appcorreios22/rastreio.py", line 74, in <module>
    status = rastrear_objeto(cod)
File "/mount/src/appcorreios22/rastreio.py", line 23, in rastrear_objeto
    driver = webdriver.Chrome(options=chrome_options)
File "/home/adminuser/venv/lib/python3.13/site-packages/selenium/webdriver/chrome/webdriver.py", line 47, in __init__
    super().__init__(
    ~~~~~~~~~~~~~~~~^
        browser_name=DesiredCapabilities.CHROME["browserName"],
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
        keep_alive=keep_alive,
        ^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.13/site-packages/selenium/webdriver/chromium/webdriver.py", line 58, in __init__
    self.service.start()
    ~~~~~~~~~~~~~~~~~~^^
File "/home/adminuser/venv/lib/python3.13/site-packages/selenium/webdriver/common/service.py", line 108, in start
    self.assert_process_still_running()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
File "/home/adminuser/venv/lib/python3.13/site-packages/selenium/webdriver/common/service.py", line 121, in assert_process_still_running
    raise WebDriverException(f"Service {self._path} unexpectedly exited. Status code was: {return_code}")
