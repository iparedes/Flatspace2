import pygame as pg
import pygame_textinput

CONSOLE_MARGIN=10

MAX_BUFFER=5

class Console:
    def __init__(self,width,height):
        self.textinput=pygame_textinput.TextInput(initial_string="",font_size=14,text_color=(255,255,255))
        self.active=False
        self.area=pg.Rect(CONSOLE_MARGIN,height-self.textinput.font_size,width-(CONSOLE_MARGIN*2),self.textinput.font_size)
        self.ready=False
        self.buffer=[None]*MAX_BUFFER
        self.bufidx=-1
        self.full_buffer=False

    def draw(self,surface):
        pg.draw.rect(surface,(32,32,32),self.area)
        surface.blit(self.textinput.get_surface(), (self.area.left,self.area.top+2))

    def update(self,events):
        k=self.textinput.update(events)
        if k==pygame_textinput.KEY_RETURN:
            t = self.textinput.get_text()
            self.textinput.clear_text()
            self.textinput.get_surface().fill((32, 32, 32))

            self.bufidx+=1
            self.buffer[self.bufidx]=t
            if self.bufidx==MAX_BUFFER:
                self.full_buffer=True
                self.bufidx=0
            return True
        elif k==pygame_textinput.KEY_UP:
            self.bufidx-=1
            if self.bufidx<0:
                if self.full_buffer:
                    self.bufidx=MAX_BUFFER-1
                else:
                    self.bufidx=self.buffer.index(None)-1
            self.textinput.set_text(self.buffer[self.bufidx])
        return False



    def get_text(self):
        if self.bufidx>=0:
            t=self.buffer[self.bufidx]
        else:
            t=''
        return t




