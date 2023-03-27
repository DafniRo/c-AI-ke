#EDITOR PLUGIN, USE AS GUIDELINE ON HOW TO USE QWIDGET



class Editor_Widget(QWidget):
    """This doct widget is an editor in which, given the layer of previously predicted events, it can edit (add/delete) events
    Parameters
    ----------
    napari_viewer : napari.Viewer
        the viewer that the editor will edit the events from
    """
    def __init__(self, napari_viewer, nbh_size = 10):
        super().__init__()
        self._viewer: napari.Viewer = napari_viewer
        self.setLayout(QVBoxLayout())
        self.nbh_size = nbh_size
        self.time_data = None
        self.image_path = None

        self.eda_layer = None
        self.eda_ready = False
        self.on_off_score = 0
        self.undo_score = 0
        self.undo_arr = np.zeros((10,2048,2048))

        self.create_EDA_layer_selector()

        self.create_size_slider()

        self.create_top_buttons()

        self.event_list = QListWidget()

        self.create_bottom_buttons()

        self.layout().addLayout(self.choose_eda_line)
        self.layout().addLayout(self.size_grid)
        self.layout().addLayout(self.top_btn_layout)
        self.layout().addWidget(self.event_list)
        self.layout().addLayout(self.bottom_btn_layout)

        if len(self._viewer.layers) > 0:
            self.init_data()

        self.Twait=2500
        self.timer=QTimer()
        self.timer.setInterval(self.Twait)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.init_data)

      #events
        self._viewer.layers.events.inserted.connect(self.init_after_timer)
        #self.edit_btn.clicked.connect(self.get_coordinates)
        self._viewer.layers.events.removed.connect(self.eliminate_widget_if_empty)

        self._viewer.layers.events.inserted.connect(self.update_eda_layer_chooser)
        self._viewer.layers.events.removed.connect(self.update_eda_layer_chooser)
        #self._viewer.mouse_drag_callbacks.append(self.get_coordinates)
        
        @self._viewer.mouse_drag_callbacks.append
        def get_event(viewer, event):
            print('mouse down')
            dragged = False
            yield
            # on move
            while event.type == 'mouse_move':
                dragged = True
                yield
            if dragged:
                print('drag end')
            else:
                print('clicked!')
                self.get_coordinates(event.position)
        
    # Functions for the GUI creation
    def hideEvent(self, event):
        self._viewer: napari.Viewer = None
        self.nbh_size = None
        self.time_data = None
        self.image_path = None

        self.eda_layer = None
        self.eda_ready = False
        self.on_off_score = 0
        self.undo_score = 0
        event.accept()
        print('Editor Widget is closed now')


    def create_EDA_layer_selector(self):
        """Creates the selector for the EDA layer"""
        self.choose_eda_line = QHBoxLayout()
        self.choose_eda_line.addWidget(QLabel('NN Images layer'))
        self.eda_layer_chooser = QComboBox()
        for lay in self._viewer.layers:
            self.eda_layer_chooser.addItem(lay.name)
        self.choose_eda_line.addWidget(self.eda_layer_chooser)

    def update_nbh_size_from_edit(self):
        if self.neigh_edit.text().isnumeric():
            self.nbh_size = int(self.neigh_edit.text())

    def create_size_slider(self):
        self.size_grid = QGridLayout()
        self.size_slider= QScrollBar(Qt.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setSingleStep(1)
        self.size_slider.setMaximum(10)
        self.size_slider.setMinimumWidth(150)
        self.size_grid.addWidget(QLabel('Gaussian Size'),0,0)
        self.size_show = QLabel('-')
        self.size_grid.addWidget(self.size_show,0,1)
        self.size_grid.addWidget(self.size_slider,1,0,1,2)

    def create_top_buttons(self):
        self.edit_btn = QPushButton('Edit')
        self.undo_btn = QPushButton('Undo')
        self.edit_btn.setStyleSheet(""" background-color: "None"; """)
        self.undo_btn.setStyleSheet(""" QPushButton {background-color: "None";} QPushButton:pressed { background-color: "darkGray";} """)
        self.top_btn_layout = QHBoxLayout()
        self.top_btn_layout.addWidget(self.edit_btn)
        self.top_btn_layout.addWidget(self.undo_btn)
        self.edit_btn.clicked.connect(self.on_off)
        self.undo_btn.clicked.connect(self.undo)

    def create_bottom_buttons(self):
        self.save_all_btn = QPushButton('Save Image')
        self.bottom_btn_layout = QHBoxLayout()
        self.bottom_btn_layout.addWidget(self.save_all_btn)
        self.save_all_btn.clicked.connect(self.save_all_events)
    
    ##### BUTTON HAS ON-OFF STATES WITH DIFFERENT ON_OFF_SCORE #####
    def on_off(self):
        if self.on_off_score == 0:
            self.on_off_score = self.on_off_score+1
            self.edit_btn.setStyleSheet(""" background-color: "darkGray"; """)
            gauss=self.get_gaussian(2,3)
        elif self.on_off_score == 1:
            self.on_off_score = self.on_off_score-1
            self.edit_btn.setStyleSheet(""" background-color: "None"; """)
        # self.edit_btn.setCheckable(True);
        # self.edit_btn.setStyleSheet(QString("QPushButton {background-color: gray;}"));

    ##### EDA LAYER: CHOOSING LAYER ---> EDA_LAYER UPDATES #####
    def update_eda_layer_from_chooser(self, text = None):
        if text is None:
            self.search_eda_layer()
            text = self.eda_layer_chooser.currentText()
        if text != '':
            self.eda_layer = self._viewer.layers[text]
            self.size_slider.setValue(5)
            self.eda_ready = True

    ##### EDA LAYER: IF LAYER IS ADDED OR REMOVED ---> CHOOSER OPTIONS UPDATE #####
    def update_eda_layer_chooser(self):
        self.eda_layer_chooser.clear()
        for lay in self._viewer.layers:
            self.eda_layer_chooser.addItem(lay.name)
    
    ##### EDA LAYER: LOOK THROUGH AVAILABLE LAYERS AND CHECK IF A LAYER IS CALLED 'NN IMAGES' ---> EDA_LAYER BECOMES 'NN IMAGES' #####
    def search_eda_layer(self):
        self.eda_ready = False
        for lay in self._viewer.layers:
            if lay.name == 'NN Images':
                self.eda_layer = lay
                self.eda_ready = True
                try:
                    self.eda_layer_chooser.setCurrentText('NN Images')
                except:
                    print('No compatible layer in the selector')
        if not self.eda_ready:
            self._viewer.add_image(np.zeros(self._viewer.layers[0].data.shape), name="NN Images", blending="additive", 
                                   scale=self._viewer.layers[0].scale, colormap='red')
            self.update_eda_layer_chooser()
            self.update_eda_layer_from_chooser()            
    
    ##### SAVE #####
    def save_all_events(self):
        for lay in self._viewer.layers:
            data=self.eda_layer.data
            currname= f'{lay.name}_edit.tiff'
            directory = r'C:\Users\roumba\Documents\Software\deep-events'
            savepath = directory + f'\{currname}'
            tifffile.imwrite(savepath, (data).astype(np.uint64), photometric='minisblack')
        

    ##### UPDATE #####
    def update_event_labels(self):
        data = np.zeros(self.eda_layer.data.shape, dtype = np.int8)
        dims = len(data.shape)
        for i in range(self.event_list.count()):
            lims = self.event_list.itemWidget(self.event_list.item(i)).get_corrected_limits()
            if dims == 4:
                data[lims[0][0]:lims[0][1],lims[1][0]:lims[1][1],lims[2][0]:lims[2][1],lims[3][0]:lims[3][1]] = i+1
            else:
                data[lims[0][0]:lims[0][1],lims[2][0]:lims[2][1],lims[3][0]:lims[3][1]] = i+1
        if self._viewer.layers.__contains__('Event Labels'):
            self._viewer.layers['Event Labels'].data = data
        else:
            self._viewer.add_labels(data = data, name='Event Labels')


    ##### DEFINE THE GAUSSIAN POINTS GENERATION #####
    def get_gaussian(self, sigma, sz):
        size= (sz,sz)
        mu=(sz/2,sz/2)
        mu = ((mu[1]+0.5-0.5*size[1])/(size[1]*0.5), (mu[0]+0.5-0.5*size[0])/(size[0]*0.5))
        sigma = (sigma/size[0], sigma/size[1])
        mvn = tfp.distributions.MultivariateNormalDiag(loc=mu, scale_diag=sigma)
        x,y = tf.cast(tf.linspace(-1,1,size[0]),tf.float32), tf.cast(tf.linspace(-1,1,size[1]), tf.float32)
        coords = tf.reshape(tf.stack(tf.meshgrid(x,y),axis=-1),(-1,2)).numpy()
        gauss = mvn.prob(coords)
        return tf.reshape(gauss, size)
    
    ##### ADD #####
    def add_gauss(self,sz):
        """ Function that adds Gaussian intensity from NN Images """
        sigma = self.size_slider.value()
        gaussian_points = self.get_gaussian(sigma,sz)  
        gaussian_points = gaussian_points.numpy()                                                               #convers tensor into numpy array
        gaussian_points = gaussian_points/np.max(gaussian_points)                                               #divides by the max
        gaussian_points[gaussian_points < 0.1] = 0                                                              #sets background to zero
        gaussian_points = gaussian_points/np.max(gaussian_points)                                               #divides by max again
        return gaussian_points

    ##### REMOVE SQUARES #####
    def remove_int(self,mu,fr_num):
        """ Function that removes intensity from NN Images """
        sigma = self.size_slider.value() 
        # xmax=mu[1]+sigma  
        # xmin=mu[1]-sigma
        # ymax=mu[0]+sigma
        # ymin=mu[0]-sigma
        self.eda_layer.data[fr_num, :, :] = flood_fill(self.eda_layer.data[fr_num], (mu[0], mu[1]), 0, tolerance=0.15)                                                                                        #divides by max again
        #self.eda_layer.data[fr_num, ymin:ymax, xmin:xmax] = 0
        new_data = self.eda_layer.data
        return new_data
    
        ##### UNDO BUTTON #####    
    def undo(self):
        frame_num = int(getattr(self.eda_layer, 'position')[0])
        if self.undo_score != 0:
            self.undo_score = self.undo_score - 1
            self.eda_layer.data[frame_num] = self.undo_arr[self.undo_score]
            self.eda_layer.refresh()
        else:
            print('Undo unavailable')

    def get_coordinates(self, data_coordinates):
        data_coordinates = [data/scale for data, scale in zip(data_coordinates, self._viewer.layers[0].scale)]
        if self.on_off_score==1:
            frame_num = round(data_coordinates[0])
            print("DATA COORDS", data_coordinates)
            ycoord = data_coordinates[1]
            xcoord = data_coordinates[2]
            self.undo_arr[self.undo_score]= self.eda_layer.data[frame_num]
            mu = (ycoord,xcoord)
            size = 50
            pixel_coords = [round(x) for x in data_coordinates]
            print("PIXEL COORDS", pixel_coords)
            int_val = self.eda_layer.data[pixel_coords[0],pixel_coords[1],pixel_coords[2]]
            if  int_val < 0.1:
                xmax=round(pixel_coords[2]+(size/2))
                xmin=round(pixel_coords[2]-(size/2))
                ymax=round(pixel_coords[1]+(size/2))
                ymin=round(pixel_coords[1]-(size/2))
                print('Intensity Value is', int_val)
                self.eda_layer.data[frame_num, ymin:ymax, xmin:xmax] = self.eda_layer.data[frame_num, ymin:ymax, xmin:xmax] + self.add_gauss(size)
                self.undo_score=self.undo_score+1
                if self.undo_score==10:
                    for i in range(1,10):
                        self.undo_arr[i-1]=self.undo_arr[i]
                    self.undo_score=9
            else: 
                print('Intensity Value is', int_val)
                mu = [round(x) for x in mu]
                self.eda_layer.data = self.remove_int(mu,frame_num)
                self.undo_score=self.undo_score+1
                if self.undo_score==10:
                    for i in range(1,10):
                        self.undo_arr[i-1]=self.undo_arr[i]
                    self.undo_score=9
            self.eda_layer.refresh()

    ##### SLIDER VALUE SHOWN #####
    def update_size(self):
        self.size= self.size_slider.value()
        self.size_show.setText(str(self.size))


    ##### INITIALIZING THE DATA #####
    def init_data(self):
        """Initialize data from the layers"""

        self.update_eda_layer_chooser()
        self.eda_layer_chooser.currentTextChanged.connect(self.update_eda_layer_from_chooser)
        self.update_eda_layer_from_chooser()
        self.size_slider.valueChanged.connect(self.update_size)
        self.size_slider.setValue(5)
        if self.eda_ready:
            self.update_size()
        self.undo_arr = np.zeros([10] + list(self._viewer.layers[self.eda_layer_chooser.currentText()].data.shape[1:]))


    def eliminate_widget_if_empty(self,event):
        if len(event.source)==0:
            try:
                self._viewer.window.remove_dock_widget(self)
                self.image_path=None
            except:
                print('Dock already deleted')

    def init_after_timer(self): ##wooow directly put in connect
        if len(self._viewer.layers) < 2:
            self.timer.start(self.Twait) #restarts the timer with a timeout of Twait ms