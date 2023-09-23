from .gologin import GoLogin
import pyppeteer
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal
import tracemalloc
import random
from urllib.parse import urlparse
import traceback
# tracemalloc.start()
class WorkerThread(QObject):
    iMess = pyqtSignal(dict)  # Tín hiệu để truyền kết quả về cho UI thread
    
    def __init__(self):
        super().__init__()
        self.elAmzClick = None

    async def runAtuo(self,browser,row,profileId):
        try:
            # https://aax-us-iad.amazon.com/x/c/...
            # browser.on('disconnected', await self.on_disconnected(browser,gl))
            # try:
                # tracemalloc.start()  # Bắt đầu theo dõi việc cấp phát bộ nhớ
            # await page.goto('https://www.amazon.com')
            all_tabs = await browser.pages()
            print(f"count tab: {len(all_tabs)}")
            check_url = None
            if len(all_tabs) > 1:
                # current_tab = len(all_tabs)-4
                # page = all_tabs[current_tab]
                for tab in all_tabs:
                    current_url = tab.url
                    # print(f"parsed_url: {current_url}")
                    parsed_url = urlparse(current_url)
                    if parsed_url.netloc == 'www.amazon.com':
                        page = tab
                        await page.bringToFront()
                        check_url = 'www.amazon.com'
                        break
                    else:
                        page = await browser.newPage()
            else:
                page = await browser.newPage()
                
            page.setDefaultNavigationTimeout(100000)    
            # await self.select_item(page)
            
            # snapshot = tracemalloc.take_snapshot()
            # top_stats = snapshot.statistics('lineno')
            # return
            
            if check_url != 'www.amazon.com':
                await self.gg_search(page)
                if await self.check_throttle_message(page):
                    await self.timeout(3)
                    await page.reload()
                    await self.timeout(5)
                # Lấy thông tin về việc cấp phát bộ nhớ (tùy chọn)
                # snapshot = tracemalloc.take_snapshot()
                # top_stats = snapshot.statistics('lineno')
                # for stat in top_stats[:10]:
                    # print(stat)
                    
            retry_times=500
            # Khu vực test function
            # await self.click_list_img(page)
            # return
            for index in range(retry_times):
                print(f"Vòng lập: {index+1}")
                res = {'count_loop': index+1,'row':row,'profile_id':profileId}
                self.iMess.emit(res)
                try:
                    await self.timeout(5)
                    getKeyword = await self.random_keyword()
                    
                    random_res = await self.random_view_item(0,50)
                    print(f"Random search: {random_res}")
                    if random_res < 1:
                        await self.search_keyworks(page,getKeyword)
                        await self.auto_scroll(page)
                        await self.timeout(5)
                        
                        await self.select_item(page)
                        await self.timeout(5)
                        
                        await self.click_list_img(page)
                        await self.timeout(5)
                        
                        await self.auto_scroll(page)
                        
                        await self.view_img_comment(page)
                        await self.timeout(5)
                        
                        await self.random_click_sequence(page)
                        await self.timeout(5)
                        
                    else:
                        await self.click_list_img(page)
                        await self.timeout(5)
                        
                        await self.auto_scroll(page)
                        
                        await self.view_img_comment(page)
                        await self.timeout(5)
                        
                        await self.random_click_sequence(page)
                        await self.timeout(5)
                        
                except Exception as e:
                    if "Session closed. Most likely the page has been closed." in str(e):
                        print("The browser session has been closed!")
                        res = {'row':thisProcess['row'],'isStatus':"Browser Closed!"}
                        self.iMess.emit(res)
                        await browser.close()
                        await gl.stoop()
                        # Thực hiện các hành động cần thiết khi biết session đã bị đóng
                    else:
                        print(f"An unexpected error occurred: {e}")
                
                print(f"Kết thúc vòng lập: {index+1}")
                res = {'count_loop_end': index+1,'row':row,'profile_id':profileId}
                self.iMess.emit(res)
            # await browser.close()
            # gl.stop()
        except Exception as b:
            print(f"Connection error, retrying...{b}")
        
    async def check_tab(self,page):
        current_url = page.url()
        
    async def random_view_item(self,min_val, max_val,exclude=[]):
        while True:
            rand_num = random.randint(min_val, max_val)
            if rand_num not in exclude:
                return rand_num
            
    async def timeout(self,seconds):
        await asyncio.sleep(seconds)

    async def on_disconnected(self,browser,gl):
        await browser.close()
        gl.stop()
        print("Trình duyệt đã ngắt kết nối!")
        
    async def gg_search(self,page):
        rand_page_gg = await self.random_view_item(1, 10)
        element_page_gg = f'#search > div:nth-child(1) > #rso > div:nth-child({rand_page_gg}) > div > div > div > div > div'
        # print(element_page_gg)
        res = {'msg': 'GG Search!','isStatus':'running...'}
        self.iMess.emit(res)
        attempts = 0
        
        getKeyword = await self.random_keyword()
        await page.goto('https://google.com')
        await page.waitForSelector('#APjFqb')
        await page.type('#APjFqb',getKeyword+" site:amazon.com",delay=100);
        await page.keyboard.press('Enter'); 
        await page.waitForNavigation({ 'waitUntil': 'networkidle0' })
        await page.waitForSelector('#search')

        # div_elements = await page.querySelectorAll('#search > div:nth-child(1) > #rso')
        # await get_dom_path_to_search
        # else:
        while not await self.check_selector(page, element_page_gg,True) and attempts < 20:
            print("Không tìm thấy đường dẫn nào phù hợp."+element_page_gg)
            rand_page_gg = await self.random_view_item(1, 20)
            # element_page_gg = f'#search > div:nth-child(1) > #rso > div:nth-child({rand_page_gg}) > div:nth-child(1) > div > div > div > div > div'
            element_page_gg = f'#search > div:nth-child(1) > #rso > div:nth-child({rand_page_gg}) > div:nth-child(1)'
            print("Đang đợi selector..."+element_page_gg)
            await asyncio.sleep(1)  # Đợi 1 giây trước khi kiểm tra lại
            attempts += 1
            
        await page.waitForSelector(element_page_gg)
        await page.click(element_page_gg)
        
    async def check_throttle_message(self,page):
        try:
            content = await page.evaluate('''() => {
                let element = document.querySelector("pre");
                return element ? element.textContent : null;
            }''')
            if content == "Request was throttled. Please wait a moment and refresh the page":
                return True
        except ZeroDivisionError:
            print("Division by zero error caught!")
        return False
        
    async def is_last_element_a_tag(self,page,selector):
        result = await page.evaluate('''(selector) => {
            const parentElement = document.querySelector(selector);
            if (parentElement) {
                const findElement = parentElement.textContent;
                if(findElement.includes('https://www.amazon.com')){
                   return findElement
                }else{
                    return false
                }
            } 
            return false;
        }''',selector)
        print(result)
        return result
    
    async def check_selector(self,page, selector, exept = False):
        print(f"selector: {selector}")
        el_exists = await page.querySelector(selector)
        print(f"el: {bool(el_exists)}")
        if exept:
            if el_exists:
                hrefAmz = await self.is_last_element_a_tag(page,selector)
                if not hrefAmz:
                    return False
        return bool(el_exists)
        
    async def select_item(self,page):
        await page.bringToFront()
        rand_page_amz = await self.random_view_item(9, 25)
        rand_page_amz2 = await self.random_view_item(1, 5)
        elemt_search_box = 'div.s-search-results'
        child_index = 5  # Thay đổi chỉ mục của child (bắt đầu từ 0)

        child_count = await page.evaluate('''(selector) => {
            const element = document.querySelector(selector);
            return element ? element.children.length : 0;
        }''', elemt_search_box)

        print(f'Số phần tử: {child_count}')
        
        random_item = await self.random_view_item(child_index, child_count)
        itemk_index = f'{elemt_search_box} > :nth-child({random_item})'

        print(itemk_index)

        # await self.timeout(5)

        # item_index = await self.check_selector(page, itemk_index)
        attempts=0
        retry_times=3
        for _ in range(retry_times):
            try:
                while not await self.get_item_res_amz(page) and attempts < 20:
                    # print(itemk_index)
                    print('Không tìm thấy item Index, thực hiện vòng lập...')
                    # random_item = await self.random_view_item(child_index, child_count)
                    # itemk_index = f'{elemt_search_box} > :nth-child({random_item})'
                    await asyncio.sleep(1)  # Đợi 1 giây trước khi kiểm tra lại
                    attempts += 1
                
                # lastEl = await self.check_item_res_search(page,itemk_index)
                print(f'Scroll to element: {self.elAmzClick}')
                # await self.scroll_to_element(page,self.elAmzClick)
                # await page.waitForSelector(self.elAmzClick)
                # await page.click(self.elAmzClick)
                await self.timeout(8)
                return
            except Exception as e:
                # Nếu xảy ra lỗi, chờ một lúc rồi thử lại
                print(f"Error: {e}")
                print("Không thể click vào element sau", retry_times, "lần thử.")
                traceback.print_exc()
                await asyncio.sleep(2)  # Chờ 2 giây trước khi thử lại

        
    
    async def random_keyword(self):
        file_path = 'keyword.txt'
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        keyword_arr = [line.strip() for line in lines]
        return random.choice(keyword_arr)
    
    
    async def get_item_res_amz(self, page):
        await page.bringToFront()
        elemt_search_box = await page.JJ('div.s-product-image-container')
        
        # print(f"Selected element: {elemt_search_box}")
        if not elemt_search_box:
            print("No elements found!")
            return None

        random_view = await self.random_view_item(0, len(elemt_search_box))
        selected_element = elemt_search_box[random_view]

        print(f"Selected element index: {random_view}")
        # print(f"Total elements: {len(elemt_search_box)}")
        print(f"Selected element: {selected_element}")

        try:
            # Scrolling the element into view
            await page.evaluate('(element) => { element.scrollIntoView() }', selected_element)
            await page.waitFor(1000)
            await selected_element.click()
        except Exception as e:
            print(f"Error while clicking the element: {e}")
            selected_element = None

        print(f"selector to click: {self.elAmzClick}")
        return selected_element


    async def search_keyworks(self,page, keywork):
        await page.bringToFront()
        sltinput = 'form[role="search"]'
        checkslt = await self.check_selector(page, sltinput)  # Assuming check_selector is similar to your JS version
        
        if checkslt:
            keyboard = page.keyboard
            await asyncio.sleep(1)
            await page.waitForSelector(sltinput)
            await page.click(sltinput)

            # Press Ctrl + A (Select All)
            await keyboard.down('Control')
            await keyboard.press('A')
            await keyboard.up('Control')

            # Press Backspace (Delete)
            await keyboard.press('Backspace')
            await asyncio.sleep(3)

            await page.type(sltinput, keywork, delay=100)
            await keyboard.press('Enter')  # Enter Key
            await page.waitForNavigation()
        else:
            print('Error Search!')
            await page.goto('https://www.amazon.com')
            return False


    async def auto_scroll(self,page):
        await page.bringToFront()
        max_scrolls = await self.random_view_item(15,80)
        print(f'Scroll page: {max_scrolls}')
        await page.evaluate('''(maxScrolls) => {
            return new Promise((resolve) => {
                let totalHeight = 0;
                let distance = Math.floor(Math.random() * (250 - 100 + 1) + 100);  // Khoảng cách scroll ngẫu nhiên từ 100 đến 250
                let scrolls = 0;  // scrolls counter
                const timer = setInterval(() => {
                    const scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    scrolls++;  // increment counter
                    
                    console.log('Scroll page: ' + timer);
                     // stop scrolling if reached the end or the maximum number of scrolls
                    if (totalHeight >= scrollHeight - window.innerHeight || scrolls >= maxScrolls) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 500);
            });
        }''', max_scrolls)
    async def scroll_to_top(self,page):
        await page.evaluate('''() => {
           window.scrollTo(0, 0);
        }''')
        
    async def hover_to_zoom(self, page, el="#imgTagWrapperId"):
        await page.bringToFront()
        # Lấy tọa độ của element dựa trên id
        element = await page.J(el)
        box = await element.boundingBox()

        # Định nghĩa số bước di chuyển và khoảng cách giữa mỗi bước
        steps = random.randint(8, 12)  # Ngẫu nhiên số lượng bước từ 8 đến 12
        # Bắt đầu từ vị trí giữa chiều rộng và phía trên của hình
        # current_x = box['x'] + box['width'] / 2
        # current_y = box['y']
        # Di chuyển chuột ngẫu nhiên trên hình ảnh
        try:
            for i in range(steps):
                current_x = random.uniform(box['x'], box['x'] + box['width'])
                current_y = random.uniform(box['y'], box['y'] + box['height'])

                await page.mouse.move(current_x, current_y)
                await page.waitFor(random.randint(200, 400))  # Ngẫu nhiên thời gian chờ từ 200 đến 400 ms

            # Đợi một chút ở vị trí cuối cùng để ảnh có thời gian phản hồi
            await page.waitFor(1000)
        except:
            print(f"Error click zoom")
    
    async def click_list_img(self, page):
        await page.bringToFront()
        element = await page.J("div#imgTagWrapperId > img") # click vao img de mo popver
        try:
            #check popver co mở không
            await element.click()
            await page.waitFor(5000)
            check_pop = 'div#a-popover-lgtbox'
            # display_value = await page.evaluate('''(check_pop) => {
                # const element = document.querySelector(check_pop);
                # if (element) {
                    # const style = window.getComputedStyle(element);
                    # return style.display;
                # }
                # return null;
            # }''', check_pop)
            # if display_value == "none" :
                # await element.click()
                # await page.waitFor(3000)
                # print(f"Click open pop img") 
                
            # lay danh sach img trong popver
            el_pop_img = await page.JJ('div.ivThumb')
            print(f"list pop img : {len(el_pop_img)}") 
            
            for el in el_pop_img[2:-2]:
                try: 
                    content = await page.evaluate('(el) => el.innerHTML', el)
                    print(f"Click element : {content}")
                    await el.click()
                    print(f"Click img : {el}") 
                    await page.waitFor(5000)
                    
                    el_zoom_img = await page.J("div#ivLargeImage > img") #click to zoom img
                    # print(f"Click zoom img : {el}") 
                    zoom_img = await page.evaluate('(el_zoom_img) => el_zoom_img.innerHTML', el_zoom_img)
                    print(f"Click element : {zoom_img}")
                    await el_zoom_img.click()
                    await page.waitFor(1000)
                    
                    await self.hover_to_zoom(page, "div#ivLargeImage > img")
                    print(f"hover_to_zoom img : {el}") 
                    await page.waitFor(3000)
                
                    rand_view = random.randint(0, 25)
                    print(f"random click tiếp : {rand_view}") 
                    if rand_view < 6:
                        break
                except Exception as e:
                    content = await page.evaluate('(el) => el.innerHTML', el)
                    print(f"Error Element img loop : {content}")
                    print(f"Error click img loop : {e}")    
            
            el_close_pop_img = await page.J('button[class=" a-button-close a-declarative a-button-top-right"]')
            await el_close_pop_img.click()
        except Exception as e:
            print(f"Error click item one page : {e}")    
            
    
    async def view_img_comment(self, page):
        await page.bringToFront()
        try:
            j_popup = await page.J('a[class="a-link-emphasis"]')
            if j_popup:
                await j_popup.click()
                await page.waitFor(8000)
            else:
                print("j_popup element not found!")
                return

            count_img = await page.JJ('div[class="cr-thumbnail-preview-tile"]')
            click_next = await page.J('div.cr-lightbox-navigator-button.cr-lightbox-navigator-button__next[style]')
            
            print(f"count_img: {len(count_img)}")  # Print the number of images, not the element list
            # print(f"click_next: {click_next}")  
            zoom_img = await page.evaluate('(el_zoom_img) => el_zoom_img.innerHTML', click_next)
            print(f"click_next : {zoom_img}")
            if count_img:
                await count_img[0].click()
                num_imgs = len(count_img) if len(count_img) <= 15 else 15
                for index in range(num_imgs - 2):
                    print(f"click_next view cmt : {index}")
                    if click_next:
                        await click_next.click()
                        await page.waitFor(random.randint(3000, 6000))
                    else:
                        print("click_next element not found!")
                        break

            # Close popup
            el_close_pop_img = await page.J('button[class=" a-button-close a-declarative"]')
            if el_close_pop_img:
                await el_close_pop_img.click()
            else:
                print("el_close_pop_img element not found!")
                
        except Exception as e:
            print(f"Error click view img comment : {e}")
  
    
    async def random_row_items(self, page):
        try:
            jj_rows = await page.JJ('div[class="a-row a-carousel-controls a-carousel-row a-carousel-has-buttons"]')
            
            attempts = 10  # Giới hạn số lần thử
            for _ in range(attempts):
                try:
                    rand = random.randint(0, len(jj_rows) - 1)
                    rand_row = jj_rows[rand]
                    j_next = await rand_row.J("div[class=\"a-carousel-row-inner\"] > div[class=\"a-carousel-col a-carousel-right\"]")
                    if j_next:
                        await page.evaluate('(element) => { element.scrollIntoView(); }', rand_row)
                        return rand_row
                except Exception as e:
                    print(f"Error in random attempt: {e}")
            print("Exceeded maximum attempts to find the element.")
                    
        except Exception as e:
            print(f"Error click view img comment : {e}")   
    
    async def random_click_sequence(self, page):
        await page.bringToFront()
        # Selector cho nút "next" và "pre"
        rand_loop = random.randint(2, 5)
        print(f"rand_loop total:{rand_loop}")
        element_to_click = None
        error_click = 0
        for index in range(rand_loop):
            print(f"rand_loop:{index}")
            this_row = await self.random_row_items(page)
            if not this_row:
                print("Không tìm thấy row click!.")
                return
            try:   
                total_clicks = random.randint(3, 5)
                print(f"total_clicks:{total_clicks}")
                # child_next_pre = 'div[class="a-carousel-row-inner"] > div[class="a-carousel-col a-carousel-right"]'
                next_selector = await this_row.J(f'.a-button.a-button-image.a-carousel-button.a-carousel-goto-nextpage')

                # Khởi tạo số lần click 'next' và 'prev'
                next_count = 0
                prev_count = 0

                # Đảm bảo lần đầu tiên là 'next'
                await next_selector.click()
                await page.waitFor(5000)
                next_count += 1
                pre_selector = await this_row.J(f'.a-button.a-button-image.a-carousel-button.a-carousel-goto-prevpage')
                print(f"prev:{pre_selector}")
                for _ in range(total_clicks - 1):  # Trừ đi lần đầu tiên đã click 'next'
                    print(f"click lần: {next_count}")
                    if next_count > 3 * prev_count:  # Có thể click 'next' hoặc 'prev'
                        action = random.choice(['next','next','next', 'prev'])
                        if action == 'next':
                            await next_selector.click()
                            await page.waitFor(5000)
                            next_count += 1
                        else:
                            await pre_selector.click()
                            await page.waitFor(5000)
                            prev_count += 1
                    else:  # Chỉ có thể click 'next'
                        await next_selector.click()
                        next_count += 1
                    # Thêm thời gian chờ giữa các lần click để đảm bảo trang web phản hồi đúng cách
                    await asyncio.sleep(1)
                
                child_link = await this_row.JJ('a[class="a-link-normal"]') 
                # child_link = await this_row.JJ('li[class="a-carousel-card"]') 
                # Chọn một phần tử ngẫu nhiên từ danh sách
                element_to_click = random.choice(child_link)

                # zoom_img = await page.evaluate('(el_zoom_img) => el_zoom_img.innerHTML', random_link)
                # print(f"Link Click:{zoom_img}")
                # if await self.is_element_clickable(random_link):
                # else:
                    # print("Phần tử không thể click!")
                    
            except Exception as e:
                error_click +=1
                print(f"Error choose next item : {e}")     
        
        if element_to_click:
            await element_to_click.click()   
            zoom_img = await page.evaluate('(el_zoom_img) => el_zoom_img.innerHTML', element_to_click)
            print(f"Link Click:{zoom_img}")
        
    async def is_element_clickable(self,element_handle):
        # Kiểm tra xem phần tử có đáp ứng tiêu chí để click không
        result = await element_handle.evaluate('''(element) => {
            // Kiểm tra xem phần tử có bị ẩn không
            const style = window.getComputedStyle(element);
            const isDisplayed = style.display !== "none";
            const isVisible = style.visibility !== "hidden";

            // Kiểm tra xem phần tử có nằm trong viewport không
            const rect = element.getBoundingClientRect();
            const isInViewport = (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );

            return isDisplayed && isVisible && isInViewport;
        }''')

        return result        
        
    async def click_item_sigle_page(self, page):
        # Đếm tổng số phần tử bạn muốn click
        elements1 = await page.JJ('a.a-link-normal >div> img')
        elements2 = await page.JJ('a.a-link-normal > img')
        selected_item = None
        total_elements1 = len(elements1)
        total_elements2 = len(elements2)
            
        print(f"item stt1: {total_elements1}")
        print(f"item click2: {total_elements1}")
        if total_elements1 > total_elements2:
            randItem = await self.random_view_item(6,max(6, total_elements2))
            selected_item = elements1[randItem]
        else:
            randItem = await self.random_view_item(3,max(3, total_elements2))
            selected_item = elements2[randItem]
            
        print(f"item stt: {randItem}")
        print(f"item click: {selected_item}")
        
        # Scroll đến phần tử
        await page.evaluate('(element) => { element.scrollIntoView(); }', selected_item)
        await page.waitFor(1000)  # Đợi 2 giây trước khi thực hiện hành động tiếp theo
        try:
            # await page.waitForSelector(selected_item)
            await selected_item.click()
        except Exception as e:
            print(f"Error click next item at: {e}")
    
    async def scroll_to_element(self,page, selector):
        await page.evaluate(f'''
            let element = document.querySelector('{selector}');
            if (selector) selector.scrollIntoView();
        ''')

    async def check_item_res_search(self,page, selector):
        nth_child_selector = selector
        class_name = '.s-product-image-container'
        
        find_path_script = f'''
        (nth_child_selector, class_name) => {{
            const parent_element = document.querySelector(nth_child_selector);
            if (!parent_element) {{
                return false;
            }}
            
            const last_element = parent_element.querySelector(`${{class_name}}:last-child`);
            if (!last_element) {{
                return false;
            }}
            
            let path = [];
            let el = last_element;
            while (el) {{
                if (el.classList.contains('s-search-results')) {{
                    el = null;
                }} else {{
                    const index = Array.from(el.parentNode.children).indexOf(el) + 1;
                    path.unshift(`:nth-child(${{index}})`);
                    el = el.parentNode;
                }}
            }}
            
            return `${{nth_child_selector.split(' > ')[0]}} > ${{path.join(' > ')}}`;
        }}
        '''
        
        last_child_selector = await page.evaluate(find_path_script, nth_child_selector, class_name)
        if not last_child_selector:
            print(f"Khong tim thay last child")
        print(f"Đường dẫn từ last child của {nth_child_selector} đến class name '{class_name}': {last_child_selector}")
        return last_child_selector

    async def get_dom_path_to_search(page, selector):
        script = '''
        function getDomPathToSearch(el) {
            let path = [];
            while (el && el.nodeName.toLowerCase() !== 'html') {
                let selector = el.nodeName.toLowerCase();

                if (el.id) {
                    selector += `#${el.id}`;
                    path.unshift(selector);

                    if(el.id === 'search') {
                        break;
                    }
                } else {
                    let sibling = el, nth = 1;
                    while (sibling.previousSibling) {
                        sibling = sibling.previousSibling;
                        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.nodeName.toLowerCase() === el.nodeName.toLowerCase())
                            nth++;
                    }

                    if (nth !== 1)
                        selector += `:nth-of-type(${nth})`;
                }

                path.unshift(selector);
                el = el.parentNode;
            }
            return path.join(' > ');
        }

        let element = document.querySelector(arguments[0]);
        return getDomPathToSearch(element);
        '''

        path = await page.evaluate(script, selector)
        return path