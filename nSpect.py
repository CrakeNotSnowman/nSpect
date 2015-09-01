import math
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.resources import resource_find
from kivy.uix.button import Button
from kivy.graphics.transformation import Matrix
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.opengl import *
from kivy.graphics.gl_instructions import ClearBuffers
from kivy.graphics import *
from objloader import ObjFileLoader
from kivy.logger import Logger
from rotation import SingleRotate
from kivy.uix.widget import Widget
from kivy.graphics.fbo import Fbo
from kivy.properties import ObjectProperty
#from kivy.graphics.context_instructions.Transform import Translate



class point(object):
    pointID = 0
    colorID = 0
    sizeID = 4
    shapeID = 0 
    label = "specN"
    color = ""#_set_color(0.7, 0.7, 0., id_color=(255, 255, 0))
    shape = ""#self.scene.objects['Sphere']

    def __init__(self, pointID):
        self.pointID = pointID
        self.loc = (3*random.random(),3*random.random(),3*random.random())

    def hide(pointID):
        pass
        
        
    
    


class NSpect(Widget):
    
    texture = ObjectProperty(None, allownone=True)    
    
    def __init__(self, **kwargs):

        LOP, dm = initFiles()

        #self.canvas = RenderContext(compute_normal_mat=True)
        #self.canvas.shader.source = resource_find('simple.glsl')
        self.canvas = Canvas()
        self.scene = ObjFileLoader(resource_find("testnurbs.obj"))
        self.LOP = LOP
        self.dm = dm
        
        self.meshes = []

        self.panCamera = False # KEITH EDIT
        self.pause = True # KEITH EDIT
        
        with self.canvas:
            self.fbo = Fbo(size=self.size, with_depthbuffer=True, compute_normal_mat=True, clear_color=(0., 0., 0., 0.))
            self.viewport = Rectangle(size=self.size, pos=self.pos)
        self.fbo.shader.source = resource_find('simple.glsl')
        #self.texture = self.fbo.texture
        
        # *&Y*&Y*&YH*&Y*&Y*&Y*Y&*
        # Keith: This allows keyboard interaction
        # http://stackoverflow.com/questions/22137786/
        self._keyboard = Window.request_keyboard(None, self)
        if not self._keyboard:
            return
        self._keyboard.bind(on_key_down=self.on_keyboard_down)
        # *&Y*&Y*&YH*&Y*&Y*&Y*Y&*
        
        super(NSpect, self).__init__(**kwargs)

        with self.fbo:
            #ClearBuffers(clear_depth=True)
            
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene(self.LOP, dm)
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)

        
        Clock.schedule_interval(self.update_scene, 1 / 60.)
        
        self._touches = []

    def on_size(self, instance, value):
        self.fbo.size = value
        self.viewport.texture = self.fbo.texture
        self.viewport.size = value
        self.update_glsl()

    def on_pos(self, instance, value):
        self.viewport.pos = value

    def on_texture(self, instance, value):
        self.viewport.texture = value


    def setup_gl_context(self, *args):
        #clear_buffer
        glEnable(GL_DEPTH_TEST)
        self.fbo.clear_buffer()
        #glDepthMask(GL_FALSE);

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)
        

    def update_glsl(self, *largs):
        asp = self.width / float(self.height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.fbo['projection_mat'] = proj

    def setup_scene(self, LOP, dm):
        Color(1, 1, 1, 0)

        PushMatrix()
        Translate(0, 0, -5)
        # This Kivy native Rotation is used just for
        # enabling rotation scene like trackball
        self.rotx = Rotate(0, 1, 0, 0)
        self.roty = Rotate(-120, 0, 1, 0) # here just rotate scene for best view
        self.scale = Scale(1)
                
        UpdateNormalMatrix()
        
        self.draw_elements(LOP, dm)
        
        PopMatrix()

    def draw_elements(self, LOP, dm):
        """ Draw separately all objects on the scene
            to setup separate rotation for each object
        """
        def _draw_element(m):
            Mesh(
                vertices=m.vertices,
                indices=m.indices,
                fmt=m.vertex_format,
                mode='triangles',
            )
            
        def _set_color(*color, **kw):
            id_color = kw.pop('id_color', (0, 0, 0))
            return ChangeState(
                        Kd=color,
                        Ka=color,
                        Ks=(.3, .3, .3),
                        Tr=1., Ns=1.,
                        intensity=1.,
                        id_color=[i / 255. for i in id_color],
                    )
            
        def drawPoints():
            #print len(LOPoints), "alksdjflkasjdflkasdj"
            print self.scene.objects
            for i in range(len(self.LOP)):
                PushMatrix()
                point = self.LOP[i]
                point.shape = self.scene.objects['Sphere']
                point.color = _set_color(i/10., (i+1)/10., 0., id_color=(int(255/(1+i)), int(255/(1+i)), 255))
                #temp.shape.sphere_rot = Rotate(0, i, 0, i)
                #temp.shape.sphTr = Translate(temp.loc[0],temp.loc[1],temp.loc[2])
                #msg = "scale" + str(i)
                #temp.shape.msg = Scale(0.1,.1,.1)
                point.shape.scale = Scale((i+1)/10.0,(i+1)/10.0,(i+1)/10.0)
                #temp.shape.msg.origin = (temp.loc[0],temp.loc[1],temp.loc[2])
                self.LOP[i] = point
                print point.shape
                _draw_element(point.shape)
                point.shape.scale.origin =  (point.loc[0],point.loc[1],point.loc[2])
                PopMatrix()
                
        drawPoints()
        '''
        PushMatrix()
        temp = self.LOP[0]
        self.jerry = self.scene.objects['Sphere']
        _set_color(0, 1/10, 0., id_color=(int(255), int(255), 255))
        self.jerry.scale = Scale(0.1,.1,.1)
         self.jerry.origin = (temp.loc[0],temp.loc[1],temp.loc[2])
        _draw_element(self.jerry)
        PopMatrix()

        PushMatrix()
        temp1 = self.LOP[1]
        self.Gary = self.scene.objects['Sphere']
        _set_color(0.7, 0.7, 0., id_color=(int(255), int(255), 255))
        self.Gary.scale = Scale(0.1,.1,.1)
         self.Gary.origin = (3,3,3)
        _draw_element(self.Gary)
        PopMatrix()
        '''
        '''
        # Draw sphere in the center
        sphere = self.scene.objects['Sphere']
        _set_color(0.7, 0.7, 0., id_color=(255, 255, 0))
        _draw_element(sphere)
        
        # Then draw other elements and totate it in different axis
        pyramid = self.scene.objects['Pyramid']
        PushMatrix()
        self.pyramid_rot = Rotate(0, 0, 0, 1)
        _set_color(0., 0., .7, id_color=(0., 0., 255))
        _draw_element(pyramid)
        PopMatrix()
        
        box = self.scene.objects['Box']
        PushMatrix()
        self.box_rot = Rotate(0, 0, 1, 0)
        _set_color(.7, 0., 0., id_color=(255, 0., 0))
        _draw_element(box)
        PopMatrix()

        cylinder = self.scene.objects['Cylinder']
        PushMatrix()
        self.cylinder_rot = Rotate(0, 1, 0, 0)
        _set_color(0.0, .7, 0., id_color=(0., 255, 0))
        _draw_element(cylinder)
        PopMatrix()
        '''

    '''
    An Ode:
    FUCK YOU ADHD JERRY
        JERRY IS THAT ONE LITTLE FUCKING POINT WHO MOVES
        WHICH HE IS SUPPOSE TO DO
        BUT NO OTHER FUCKING POINT WILL MOVE
        SO FUCK YOU ADHD JERRY
    '''

    def update_scene(self, *largs):
        def _draw_element(m):
            Mesh(
                vertices=m.vertices,
                indices=m.indices,
                fmt=m.vertex_format,
                mode='triangles',
            )
            
        def _set_color(*color, **kw):
            id_color = kw.pop('id_color', (0, 0, 0))
            return ChangeState(
                        Kd=color,
                        Ka=color,
                        Ks=(.3, .3, .3),
                        Tr=1., Ns=1.,
                        intensity=1.,
                        id_color=[i / 255. for i in id_color],
                    )

        def test2(point):
            #print myPoint.pointID
            
            newLoc = (0.1*random.random(),0.1*random.random(),0.1*random.random())
            oldLoc = point.shape.scale.origin
            newLoc = ( newLoc[0]-0.05+oldLoc[0], newLoc[1]-0.05+oldLoc[1], newLoc[2]-0.05+oldLoc[2] )
            #self.msg.origin = newLoc
            #print "alksdjflkasjf"
            return newLoc #myPoint

        def updateLocs(self):
        
            for i in range(len(self.LOP)):
                point = self.LOP[i]
                #point.shape.scale = Scale((i+1)/10.0,(i+1)/10.0,(i+1)/10.0)
                #point.scale.origin =  
                point.shape.scale.origin = test2(point)
                #self.LOP[i].shape.scale.origin = test2(point)
                #_draw_element(point.shape)
                #print i, self.LOP[i].shape.scale.origin
                print self.LOP[i].shape
                
            #test2(self.LOP[0])
            #self.LOP[1].shape.scale.origin=test2(self.LOP[1])
            #self.LOP[2].shape.scale.origin=test2(self.LOP[2])
            #test2(self.LOP[3])
            #test2(self.LOP[4])

            
        if not self.pause:
            #self.pyramid_rot.angle += 0.5
            #self.box_rot.angle += 0.5
            #self.cylinder_rot.angle += 0.5
            updateLocs(self)
            #test2(self.jerry, 0)
            #test2(self.Gary, 0)
        
        pass

        
    
    # =============== All stuff after is for trackball implementation =============
    def moveA(self):
        

        pass
    def moveB(self):
        pass
    def define_rotate_angle(self, touch):
        x_angle = (touch.dx/self.width)*360
        y_angle = -1*(touch.dy/self.height)*360
        return x_angle, y_angle
    
    def on_touch_down(self, touch):
        self._touch = touch
        touch.grab(self)
        self._touches.append(touch)
        
    def on_touch_up(self, touch): 
        touch.ungrab(self)
        self._touches.remove(touch)
        self.fbo.shader.source = 'select_mode.glsl'
        self.fbo.ask_update()
        self.fbo.draw()
        print self.fbo.get_pixel_color(touch.x, touch.y)
        self.fbo.shader.source = 'simple.glsl'
        self.fbo.ask_update()
        self.fbo.draw()
    
    # *O(U(U())(*U(*(******************
    # Keith: This allows keyboard interaction
    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            if self.panCamera == True:
                self.x -= 10
            else: 
                self.roty.angle += 10
        elif keycode[1] == 'right':
            if self.panCamera == True:
                self.x += 10
            else: 
                self.roty.angle -= 10
        if keycode[1] == 'up':
            if self.panCamera == True:
                self.y += 10
            else: 
                self.rotx.angle += 10
        elif keycode[1] == 'down':
            if self.panCamera == True:
                self.y -= 10
            else: 
                self.rotx.angle -= 10

        elif keycode[1] == 'i':
            self.update_glsl()                             
            SCALE_FACTOR = 0.01             
            scale = SCALE_FACTOR
            Logger.debug('Scale up')                  
            xyz = self.scale.xyz                
            if scale:
                self.scale.xyz = tuple(p + scale for p in xyz)
        elif keycode[1] == 'o':
            self.update_glsl()                             
            SCALE_FACTOR = 0.01             
            scale = SCALE_FACTOR
            Logger.debug('Scale up')                  
            xyz = self.scale.xyz  
            if scale:
                temp = tuple(p - scale for p in xyz)
                # Prevent the collection from having a negative size
                if temp[0] > 0:
                    self.scale.xyz = temp
        elif keycode[1] == 't':
            self.panCamera = not self.panCamera    
        elif keycode[1] == 'p':
            self.pause = not self.pause    
            if not self.pause:
                print "Playing"
            else:
                print "Paused"
    
    
    
    def on_touch_move(self, touch): 

        self.update_glsl()
        if touch in self._touches and touch.grab_current == self:
            if len(self._touches) == 1:
                # here do just rotation        
                ax, ay = self.define_rotate_angle(touch)
                
                self.roty.angle += ax
                self.rotx.angle += ay

            elif len(self._touches) == 2: # scaling here
                #use two touches to determine do we need scal
                touch1, touch2 = self._touches 
                old_pos1 = (touch1.x - touch1.dx, touch1.y - touch1.dy)
                old_pos2 = (touch2.x - touch2.dx, touch2.y - touch2.dy)
                
                old_dx = old_pos1[0] - old_pos2[0]
                old_dy = old_pos1[1] - old_pos2[1]
                
                old_distance = (old_dx*old_dx + old_dy*old_dy)
                Logger.debug('Old distance: %s' % old_distance)
                
                new_dx = touch1.x - touch2.x
                new_dy = touch1.y - touch2.y
                
                new_distance = (new_dx*new_dx + new_dy*new_dy)
                
                Logger.debug('New distance: %s' % new_distance)
                SCALE_FACTOR = 0.01
                
                if new_distance > old_distance: 
                    scale = SCALE_FACTOR
                    Logger.debug('Scale up')
                elif new_distance == old_distance:
                    scale = 0
                else:
                    scale = -1*SCALE_FACTOR
                    Logger.debug('Scale down')
                    
                xyz = self.scale.xyz
                
                if scale:
                    self.scale.xyz = tuple(p + scale for p in xyz)
        

class nSpectApp(App):
    def build(self):
        root = FloatLayout()
        nSpect = NSpect()
        root.add_widget(nSpect)
        return root
    print "HELLO"
        

def initFiles():
    dm = [[0, 2, 2, 5], [2,0,2,7],[2,2,0,2],[5,7,2,0]]
    LOPoints = []
    temp = point(0)
    LOPoints.append(temp)
    temp = point(1)
    LOPoints.append(temp)
    temp = point(2)
    LOPoints.append(temp)
    temp = point(3)
    LOPoints.append(temp)
    temp = point(4)
    LOPoints.append(temp)
    return LOPoints, dm
    

def main():
    nSpectApp().run()

main()
