import time
def scroll(driver, timeout):
    scroll_pause_time = timeout
    last_height = driver.execute_script("return document.body.scrollHeight")
    count = 1
    while True:
        for scrol in range(100,last_height,150):
            driver.execute_script(f"window.scrollTo(0,{scrol})")
            time.sleep(0.2)
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        if count ==3:
            break
        count=+1