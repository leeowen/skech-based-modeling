import maya.api.OpenMaya as om
import maya.cmds as cmds
from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import math,sys, os, random
sys.path.append('/usr/lib64/python2.7/site-packages')
sys.path.append('./.local/lib/python2.7/site-packages')
sys.path.append(cmds.workspace(fn=True)+'/scripts/')
import numpy as np
import curve_fitting


def maya_main_window():
    main_window_ptr=omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    
             
class CurveFittingWindowUI(QtWidgets.QWidget):
    
    def __init__(self,parent=maya_main_window()):
        super(CurveFittingWindowUI,self).__init__(parent)
        
        self.setWindowTitle("Generalized Ellipse")
        self.setMinimumSize(900, 700)
        self.setObjectName("generalizedEllipseWin")
        self.setWindowFlags(QtCore.Qt.WindowType.Dialog)
                       
        self.create_widgets()   
        self.create_layout()
        self.create_connection()
                                   
    
    def sizeHint(self):
        return QtCore.QSize(900,700)
        
        
    def minimumSize(self):
        return QtCore.Qsize(900,700)        
        
        
    def create_widgets(self):
        self.saveAsDat_button=QtWidgets.QPushButton('Save as .dat')
        self.saveAsImg_button=QtWidgets.QPushButton('Save as image')
        self.close_button=QtWidgets.QPushButton('Close')
        
        self.standardEllipse_checkBox=QtWidgets.QCheckBox('standard ellipse')
        self.standardEllipse_checkBox.setChecked(False)
        self.standardEllipse_checkBox.setVisible(False)
       
        self.generalizedEllipse_checkBox=QtWidgets.QCheckBox('generalized ellipse')
        self.generalizedEllipse_checkBox.setChecked(False)
        self.generalizedEllipse_checkBox.setVisible(False)
        
        self.originalEllipse_checkBox=QtWidgets.QCheckBox('original ellipse')
        self.originalEllipse_checkBox.setChecked(False)
        self.originalEllipse_checkBox.setVisible(False)

        self.showPointIndex_checkBox = QtWidgets.QCheckBox('show point index')
        self.showPointIndex_checkBox.setChecked(False)
        self.showPointIndex_checkBox.setVisible(False)

        self.showTangent_checkBox = QtWidgets.QCheckBox('show tangent')
        self.showTangent_checkBox.setChecked(False)
        self.showTangent_checkBox.setVisible(False)

        self.showCurvature_checkBox = QtWidgets.QCheckBox('show curvature')
        self.showCurvature_checkBox.setChecked(False)
        self.showCurvature_checkBox.setVisible(False)

        self.showCutPointCandidate_checkBox = QtWidgets.QCheckBox('show cut point candidate(s)')
        self.showCutPointCandidate_checkBox.setChecked(False)
        self.showCutPointCandidate_checkBox.setVisible(False)

        self.cut_point_label = QtWidgets.QLabel('cut point(s) list:')
        self.cut_point_lineEdit = QtWidgets.QLineEdit()
        self.cut_point_button = QtWidgets.QPushButton('Confirm')
                       
        self.radio_group=QtWidgets.QGroupBox()  
        self.manualJ_mode_radioButton=QtWidgets.QRadioButton('manual J')
        self.autoJ_mode_radioButton=QtWidgets.QRadioButton('auto J') 
        
        self.J_label=QtWidgets.QLabel('J:')
        self.J_label.setFixedWidth(50)
        sizePolicy=QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.J_label.setSizePolicy(sizePolicy)
        self.J_spinBox=QtWidgets.QSpinBox()
        self.J_spinBox.setValue(10)
        self.J_spinBox.setFixedWidth(100)
        self.J_spinBox.setMinimum(3)
        self.J_spinBox.setSingleStep(1)
        self.J_spinBox.setReadOnly(not self.manualJ_mode_radioButton.isChecked())

        self.Ea_label=QtWidgets.QLabel('Ea:') 
        self.Ea_label.setFixedWidth(50)   
        sizePolicy=QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.Ea_label.setSizePolicy(sizePolicy)    
        self.Ea_lineEdit=QtWidgets.QLineEdit()
        self.Ea_lineEdit.setFixedWidth(100)
        self.Ea_lineEdit.setMaxLength(5)
        self.Ea_lineEdit.setReadOnly(True)

        self.Em_label=QtWidgets.QLabel('Em:')
        self.Em_label.setFixedWidth(50)
        sizePolicy=QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.Em_label.setSizePolicy(sizePolicy)
        self.Em_lineEdit=QtWidgets.QLineEdit()
        self.Em_lineEdit.setFixedWidth(100)
        self.Em_lineEdit.setMaxLength(5)
        self.Ea_lineEdit.setReadOnly(True)
        
        self.canvas=Canvas()    
        sizePolicy=QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.canvas.setSizePolicy(sizePolicy) 
        
        self.lineWidth_doubleSpinBox=QtWidgets.QDoubleSpinBox()
        self.lineWidth_doubleSpinBox.setRange(1.0,5.0)
        self.lineWidth_doubleSpinBox.setValue(1.0)
        self.lineWidth_doubleSpinBox.setSingleStep(0.5)  
        self.lineWidth_doubleSpinBox.setFixedWidth(120)
        
        self.file_label=QtWidgets.QLabel('File:')
        sizePolicy=QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.file_label.setSizePolicy(sizePolicy)
        self.filePath_lineEdit=QtWidgets.QLineEdit()
        self.filePath_lineEdit.setMaximumWidth(150)
        self.file_label.setBuddy(self.filePath_lineEdit)
        sizePolicy=QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.filePath_lineEdit.setSizePolicy(sizePolicy)
        self.file_button=QtWidgets.QPushButton()
        self.file_button.setIcon(QtGui.QIcon(':fileOpen.png'))# ':' tells Qt that the following is resource file path
        self.file_button.setToolTip("Select File")
        sizePolicy=QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.file_button.setSizePolicy(sizePolicy)
        
        self.segment_label=QtWidgets.QLabel('segment method:')
        self.segment_label.setMaximumWidth(150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.segment_label.setSizePolicy(sizePolicy)
        self.segment_comboBox=QtWidgets.QComboBox()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.segment_comboBox.setSizePolicy(sizePolicy)
        self.segment_comboBox.setMaximumWidth(150)
        self.segment_comboBox.addItem('single piece')
        self.segment_comboBox.addItem('2 symmetrical halves')
        self.segment_comboBox.addItem('fragment')
        self.segment_comboBox.addItem('composite')
        
        self.range_label=QtWidgets.QLabel('range:')
        self.range_label.setMaximumWidth(150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.range_label.setSizePolicy(sizePolicy)
        self.range_slider=QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.range_slider.setSizePolicy(sizePolicy)
        self.range_slider.setMaximumWidth(150)
        self.range_slider.setMinimum(0)
        self.range_slider.setMaximum(100)
        
        self.radio_group.setVisible(False)
        self.segment_label.setVisible(False)
        self.segment_comboBox.setVisible(False)
        self.range_label.setVisible(False)
        self.range_slider.setVisible(False)
        self.saveAsDat_button.setVisible(False)
        self.saveAsImg_button.setVisible(False)
        self.cut_point_button.setVisible(False)
        self.cut_point_label.setVisible(False)
        self.cut_point_lineEdit.setVisible(False)
        

    def create_layout(self):   
        main_layout=QtWidgets.QHBoxLayout(self)
                 
        center_layout=QtWidgets.QHBoxLayout()
        center_layout.addWidget(self.canvas)              
        center_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)        
              
        # create layout for different parameters and operation buttons
        right_layout=QtWidgets.QVBoxLayout()
        
        right_layout.setContentsMargins(2,2,3,3)
        #right_layout.setSpacing(10)
        
        file_layout=QtWidgets.QHBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.filePath_lineEdit)
        file_layout.addWidget(self.file_button)
        right_layout.addLayout(file_layout)
        
        lineWidth_layout=QtWidgets.QFormLayout()
        lineWidth_layout.addRow('line width:',self.lineWidth_doubleSpinBox)
        right_layout.addLayout(lineWidth_layout)
        
        right_layout.addStretch(1)

        checkBox2_layout=QtWidgets.QVBoxLayout()
        checkBox2_layout.addWidget(self.showPointIndex_checkBox)
        checkBox2_layout.addWidget(self.showTangent_checkBox)
        checkBox2_layout.addWidget(self.showCurvature_checkBox)
        checkBox2_layout.addWidget(self.showCutPointCandidate_checkBox)
        right_layout.addLayout(checkBox2_layout)

        right_layout.addStretch(1)
        
        checkBox_layout=QtWidgets.QVBoxLayout()
        checkBox_layout.addWidget(self.standardEllipse_checkBox)
        checkBox_layout.addWidget(self.generalizedEllipse_checkBox)
        checkBox_layout.addWidget(self.originalEllipse_checkBox)
        right_layout.addLayout(checkBox_layout)
        
        right_layout.addStretch(1)
        
        segmentMethod_layout=QtWidgets.QVBoxLayout()
        segmentMethod_layout.addWidget(self.segment_label)
        segmentMethod_layout.addWidget(self.segment_comboBox)
        right_layout.addLayout(segmentMethod_layout) 
        
        right_layout.addStretch(1)    
        
        rangeSlider_layout=QtWidgets.QHBoxLayout()
        rangeSlider_layout.addWidget(self.range_label)
        rangeSlider_layout.addWidget(self.range_slider)
        right_layout.addLayout(rangeSlider_layout) 
        
        right_layout.addStretch(1)

        cutPoint_layout = QtWidgets.QVBoxLayout()
        cutPoint_layout.addWidget(self.cut_point_label)
        cutPoint_layout.addWidget(self.cut_point_lineEdit)
        cutPoint_layout.addWidget(self.cut_point_button)
        right_layout.addLayout(cutPoint_layout)

        right_layout.addStretch(1)

        grid_layout=QtWidgets.QGridLayout()
        grid_layout.addWidget(self.autoJ_mode_radioButton,0,0,1,2)
        grid_layout.addWidget(self.manualJ_mode_radioButton,1,0,1,2)
        grid_layout.addWidget(self.J_label,2,0)
        grid_layout.addWidget(self.J_spinBox,2,1)
        grid_layout.addWidget(self.Ea_label,3,0)
        grid_layout.addWidget(self.Ea_lineEdit,3,1)
        grid_layout.addWidget(self.Em_label,4,0)    
        grid_layout.addWidget(self.Em_lineEdit,4,1)
        self.radio_group.setLayout(grid_layout)
        
        right_layout.addWidget(self.radio_group)           
        
        right_layout.addStretch(1)
        
        button_layout=QtWidgets.QVBoxLayout()
        button_layout.addWidget(self.saveAsDat_button)
        button_layout.addWidget(self.saveAsImg_button)
        button_layout.addWidget(self.close_button)
        right_layout.addLayout(button_layout)
        
        center_layout.addLayout(right_layout)
        
        main_layout.addLayout(center_layout)
        

    def create_connection(self):
        self.saveAsDat_button.clicked.connect(self.save_dataFn)
        self.saveAsImg_button.clicked.connect(self.save_imageFn)
        self.file_button.clicked.connect(self.show_file_selected_dialog)
        self.close_button.clicked.connect(self.closeFn)
        self.standardEllipse_checkBox.toggled.connect(self.drawMode_standardEllipse)
        self.generalizedEllipse_checkBox.toggled.connect(self.drawMode_generalizedEllipse)
        self.originalEllipse_checkBox.toggled.connect(self.drawMode_originalEllipse)
        self.J_spinBox.valueChanged.connect(self.update_manual_J_value)
        self.lineWidth_doubleSpinBox.valueChanged.connect(self.canvas.setLineWidth)
        self.manualJ_mode_radioButton.toggled.connect(self.update_visibility_manual_J_mode)
        self.autoJ_mode_radioButton.toggled.connect(self.update_visibility_auto_J_mode)
        self.segment_comboBox.currentTextChanged.connect(self.segmentMode_change)
        self.range_slider.valueChanged.connect(self.fragment_range_change)
        self.showPointIndex_checkBox.toggled.connect(self.update_display_point_index)
        self.showCurvature_checkBox.toggled.connect(self.update_curvature)
        self.showCutPointCandidate_checkBox.toggled.connect(self.update_cut_point)
        self.showTangent_checkBox.toggled.connect(self.update_tangent)
        self.cut_point_button.clicked.connect(self.get_cut_point)
        
    
    def fragment_range_change(self,value):
        self.canvas.set_fragment_range(value/100.0)
        
        
    def segmentMode_change(self,text):
        if text=='single piece':
            self.canvas.single_piece_mode=True
            self.canvas.symmetry_mode=False
            self.canvas.fragment_mode=False
            self.canvas.composite_mode=False
            self.range_label.setVisible(False)
            self.range_slider.setVisible(False)
            self.manualJ_mode_radioButton.setVisible(True)
            self.cut_point_button.setVisible(False)
            self.cut_point_label.setVisible(False)
            self.cut_point_lineEdit.setVisible(False)
        elif text=='2 symmetrical halves':
            self.canvas.symmetry_mode=True
            self.canvas.single_piece_mode=False
            self.canvas.fragment_mode=False
            self.canvas.composite_mode=False
            self.range_label.setVisible(False)
            self.range_slider.setVisible(False)
            self.manualJ_mode_radioButton.setVisible(True)
            self.cut_point_button.setVisible(False)
            self.cut_point_label.setVisible(False)
            self.cut_point_lineEdit.setVisible(False)
        elif text=='fragment':
            self.canvas.symmetry_mode=False
            self.canvas.single_piece_mode=False
            self.canvas.fragment_mode=True
            self.canvas.composite_mode=False
            self.autoJ_mode_radioButton.setVisible(False)
            self.range_label.setVisible(True)
            self.range_slider.setVisible(True)
            self.manualJ_mode_radioButton.setVisible(True)
            self.cut_point_button.setVisible(False)
            self.cut_point_label.setVisible(False)
            self.cut_point_lineEdit.setVisible(False)
        elif text == 'composite':
            self.canvas.symmetry_mode=False
            self.canvas.single_piece_mode=False
            self.canvas.fragment_mode=False
            self.canvas.composite_mode=True
            self.range_label.setVisible(False)
            self.range_slider.setVisible(False)
            self.manualJ_mode_radioButton.setVisible(False)
            self.cut_point_button.setVisible(True)
            self.cut_point_label.setVisible(True)
            self.cut_point_lineEdit.setVisible(True)
            
        self.canvas.update()
        self.showEaEm()
                        
    
    def update_visibility_manual_J_mode(self,checked):
        self.canvas.manualJ_mode=checked
        self.canvas.autoJ_mode=not checked
        self.J_spinBox.setReadOnly(not checked)
        self.canvas.repaint()# update() prevents multiple fast repaints. call repaint() instead.
        self.showEaEm()
        
        
    def update_visibility_auto_J_mode(self,checked):
        self.canvas.autoJ_mode=checked
        self.canvas.manualJ_mode=not checked
        self.J_spinBox.setReadOnly(checked)
        self.canvas.repaint()
        self.showEaEm()
        self.J_spinBox.setValue(self.canvas.autoJ_value)
        
    
    def update_manual_J_value(self,J):
        self.canvas.setManualJ(J)
        self.canvas.repaint()
        self.showEaEm()


    def update_display_point_index(self,checked):
        self.canvas.show_point_index = checked
        self.canvas.repaint()
        

    def update_tangent(self,checked):
        self.canvas.activateTangent=checked
        self.canvas.repaint()


    def update_curvature(self,checked):
        self.canvas.activateCurvature=checked
        self.canvas.repaint()


    def update_cut_point(self,checked):
        self.canvas.activateCutPoint=checked
        self.canvas.repaint()


    def save_dataFn(self):
        dirPath=cmds.workspace(q=True, rootDirectory=True )
        dirPath+='data/'
        source_file_name = self.filePath_lineEdit.text()
        file_name = source_file_name.split('/')[-1]
        file_name = file_name.replace('Source_','')
        dirPath += file_name.split('_cross_section_')[0]
        directory = os.path.dirname(dirPath+'/'+ file_name)
        
        try:
            os.stat(directory)
        except:
            os.mkdir(directory) 
            
        FILE_FILTERS="DAT(*.dat);All Files(*.*)"
        selected_filter="DAT(*.dat)"# default filter, also store last selected filter and can be used as the default filter for next select
        file_path,selected_filter=QtWidgets.QFileDialog.getSaveFileName(self, 'save',dirPath +'/'+ file_name,FILE_FILTERS,selected_filter)
        # check if user has cancel the dialog by checking if file_path is none
        if file_path:
            f=open(file_path,"w+")
            f.write('range:')
            if self.canvas.single_piece_mode==True:
                f.write('0-360 \n')
            f.write('center: {} {}\n'.format(self.canvas.center.x(),self.canvas.center.y()))
            f.write('a: ')
            for i in self.canvas.a:
                f.write(str(i)+' ')
            f.write('\n')
            f.write('b: ')
            for i in self.canvas.b:
                f.write(str(i)+' ')
            f.write('\n')
            #f.write('angles: ')
            #for i in self.canvas.angles:
            #    f.write(str(i)+' ')
            #f.write('\n')
            f.close()
        
        
    def save_imageFn(self):
        dirPath=cmds.workspace(q=True, rootDirectory=True )
        dirPath+='images/'
        FILE_FILTERS="PNG(*.png);All Files(*.*)"
        selected_filter="PNG(*.png)"# default filter, also store last selected filter and can be used as the default filter for next select
        image_name = self.filePath_lineEdit.text()
        image_name = image_name.split('Source_')[1]
        image_name = image_name.replace('.dat','.png')
        part_name = image_name.split('_cross_section')[0]
        image_name = image_name.replace('_cross_section','_generalised_ellipse')
        dirPath += part_name+ '/'
        try:
            os.stat(dirPath)
        except:
            os.mkdir(dirPath)
        file_path,selected_filter = QtWidgets.QFileDialog.getSaveFileName(self, 'save', dirPath+image_name, FILE_FILTERS, selected_filter)
        # check if user has cancel the dialog by checking if file_path is none
        if file_path:
            a=file_path.find('.png')
            b=file_path.find('.PNG')
            if a==-1 and b==-1:
                file_path+='.png'
            file=QtCore.QFile(file_path)
            if file.open(QtCore.QIODevice.WriteOnly):
                pixmap=QtGui.QPixmap(self.canvas.size())
                self.canvas.render(pixmap)
                pixmap.save(file,"PNG")
                file.close()
            else:
                QMessageBox.warning(self,'curve fitting',tr("Cannot write file %1. \nError:%2").arg(file_path).arg(file.errorString()))
        
             
    def update_visibility_originalEllipse_mode(self,checked):
        self.radio_group.setVisible(not checked)
        self.segment_label.setVisible(not checked)
        self.segment_comboBox.setVisible(not checked)
        self.saveAsDat_button.setVisible(not checked)
        self.saveAsImg_button.setVisible(checked)


    def update_visibility_standardEllipse_mode(self,checked):
        self.saveAsImg_button.setVisible(not checked)
        
    
    def show_file_selected_dialog(self):
        dirPath=cmds.workspace(q=True, rootDirectory=True )
        FILE_FILTERS="data(*.dat);;All Files(*.*)"
        selected_filter="data(*.dat)"# default filter, also store last selected filter and can be used as the default filter for next select
        file_path,selected_filter=QtWidgets.QFileDialog.getOpenFileName(self, 'Select File',dirPath+'data',FILE_FILTERS,selected_filter)
        # check if user has cancel the dialog by checking if file_path is none
        if file_path:
            self.filePath_lineEdit.setText(file_path)
            self.standardEllipse_checkBox.setVisible(True)
            self.generalizedEllipse_checkBox.setVisible(True)
            self.originalEllipse_checkBox.setVisible(True)
            self.canvas.readFile(file_path)
            self.canvas.update()
            
        
    def closeFn(self):
        self.close() 
                
        
    def drawMode_standardEllipse(self,checked):
        self.canvas.standardEllipse=checked
        self.canvas.update()
        
        self.saveAsDat_button.setVisible(checked)
        self.saveAsImg_button.setVisible(checked)
                            
            
    def drawMode_generalizedEllipse(self,checked):
        """
        if cmds.control('generalizedEllipse'+'_checkBox',exists=True):
            ptr=omui.MQtUtil.findControl('generalizedEllipse_checkBox')
            checkBox=wrapInstance(long(ptr),QtWidgets.QCheckBox)
            value=checkBox.isChecked()
        """
        self.showPointIndex_checkBox.setVisible(checked)
        self.radio_group.setVisible(checked)
        self.segment_label.setVisible(checked)
        self.segment_comboBox.setVisible(checked)
        self.saveAsDat_button.setVisible(checked)  
        self.saveAsImg_button.setVisible(checked)  
        self.canvas.generalisedEllipse=checked
        self.canvas.update()
        
       
    def showEaEm(self):   
        s1=str(self.canvas.getEa()*100)
        s1=s1[0:4]
        s2=str(self.canvas.getEm()*100)
        s2=s2[0:4]
        self.Ea_lineEdit.setText(s1+'%')     
        self.Em_lineEdit.setText(s2+'%')
                  
        
    def drawMode_originalEllipse(self,checked):
        self.canvas.originalEllipse=checked
        self.canvas.update()

        self.showPointIndex_checkBox.setVisible(checked)
        self.saveAsDat_button.setVisible(checked)
        self.saveAsImg_button.setVisible(checked)
        self.showCurvature_checkBox.setVisible(checked)
        self.showTangent_checkBox.setVisible(checked)
        self.showCutPointCandidate_checkBox.setVisible(checked)


    def get_cut_point(self):
        str = self.cut_point_lineEdit.text()
        list = str.split(' ')
        cut_points = [int(i) for i in list]
        self.canvas.cut_curve(cut_points)
            
              
class Canvas(QtWidgets.QDialog):
    backgroundColor=QtCore.Qt.white
    Ea_criteria=0.01
    Em_criteria=0.025
    
    def __init__(self,parent=None):
        super(Canvas,self).__init__(parent)
        self.setMinimumSize(650,600)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.originalEllipse=False
        self.generalisedEllipse=False
        self.standardEllipse=False
        self.manualJ=10
        self.autoJ_value=0
        self.lineWidth=1
        self.manualJ_mode=False
        self.autoJ_mode=False
        self.single_piece_mode=True
        self.symmetry_mode=False
        self.fragment_mode=False
        self.composite_mode=False
        self.activateTangent=False
        self.activateCurvature=False
        self.activateCutPoint=False
        self.show_point_index=False

        
    def sizeHint(self):
        return QtCore.QSize(650,600)
        
        
    def minimumSize(self):
        return QtCore.Qsize(650,600)
        
        
    def setManualJ(self,j):
        self.manualJ=j
        self.update()


    def cut_curve(self,cut_points):
        self.cut_points = cut_points
        # split data for N segments
        N = len(self.cut_points)
        self.vertices_matrix = []
        self.angles_matrix = []
        self.segment_center_list = []
        tmp_vertices = []
        tmp_angles = []
        for i in range(N):
            if self.cut_points[i]<self.cut_points[(i+1)%N]:
                tmp_vertices = self.vertices[self.cut_points[i]:self.cut_points[(i+1)%N]+1]
                tmp_angles = self.angles[self.cut_points[i]:self.cut_points[(i+1)%N]+1]
            else:
                tmp_vertices = self.vertices[self.cut_points[i]:self.numPt]
                tmp_vertices.extend(self.vertices[0:self.cut_points[(i + 1) % N]+1])
                tmp_angles = self.angles[self.cut_points[i]:self.numPt]
                tmp_angles.extend(self.vertices[0:self.cut_points[(i + 1) % N]+1])
            self.vertices_matrix.append(tmp_vertices)
            self.angles_matrix.append(tmp_angles)
            tmp_center = curve_fitting.getCenter(tmp_vertices)
            self.segment_center_list.append(tmp_center)
        self.update()


    def readFile(self,file_path):
        self.vertices = []
        self.angles = []
        self.d = []
        self.d_bar = []
        self.Ea = 0.0
        self.Em = 0.0
        self.numPt = 0
        self.center = QtCore.QPointF(0.0, 0.0)
        self.fragment_range=0.0
        self.start_index=0
        self.end_index=0
        self.a=[]
        self.b=[]
        self.generalisedEllipseVertices=[]
        self.cut_points = []
        f = open(file_path,'r')
        content = f.readlines()
        for line in content:
            p=line.split()
            self.numPt+=1
            self.vertices.append(om.MVector(float(p[0]),float(p[1]),float(p[2])))
        f.close()

        self.center = curve_fitting.getCenter(self.vertices)
        self.d_bar = curve_fitting.get_d_bar(self.vertices, self.center)
        
        self.angles = curve_fitting.calculateAngle(self.vertices, self.center)
        self.tangents = curve_fitting.calculateTangent(self.vertices,self.angles)
        self.normals = curve_fitting.calculateNormal(self.tangents)
        self.curvatures = curve_fitting.calculateCurvature(self.tangents,self.angles)
        
        # split data for 2 symmetrical segments respectively
        self.a_first_half=[]
        self.b_first_half=[]
        I=self.numPt/2
        self.vertices_first_half=self.vertices[0:I+1]
        self.angles_first_half=self.angles[0:I+1]
        self.vertices_second_half=self.vertices[I:self.numPt]
        self.vertices_second_half.append(self.vertices[0])
        self.angles_second_half=self.angles[I:self.numPt]
        self.angles_second_half.append(self.angles[0])
        self.center_first_half=curve_fitting.getCenter(self.vertices_first_half)
        self.center_second_half=curve_fitting.getCenter(self.vertices_second_half)

        self.vertices_matrix=[]
        self.angles_matrix=[]
        self.segment_center_list=[]
            
    
    def setLineWidth(self,width):
        self.lineWidth=width
        self.update()
        
    
    def set_fragment_range(self,value):   
        self.fragment_range=value
        self.update()
        
         
    def paintEvent(self,evt):
        painter=QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing,True)
        # Draw the background
        painter.setBrush(Canvas.backgroundColor)
        painter.drawRect(self.rect())
        
        painter.setBrush(QtCore.Qt.NoBrush)# no fill inside the shape

        if self.originalEllipse==True:
            self.draw_originalEllipse(painter)
        
        if self.standardEllipse==True:
            self.draw_standardEllipse(painter)
                    
        if self.generalisedEllipse==True:
            self.draw_generalisedEllipse(painter)

        if self.show_point_index==True:
            self.draw_point_index(painter)
            
        painter.end()
             

    def draw_point_index(self,painter):
        for i in range(self.numPt):
            p = self.vertices[i]
            painter.drawText(p[0] * 300 + self.width() / 2., p[2] * 300 + self.height() / 2., str(i))
            painter.drawEllipse(QtCore.QPointF(p[0] * 300 + self.width() / 2., p[2] * 300 + self.height() / 2.),3,3)


    def draw_generalisedEllipse(self,painter):
        penColor=QtGui.QColor(0,80,0) 
        pen=QtGui.QPen()
        pen.setColor(penColor)
        pen.setWidthF(self.lineWidth)
        painter.setPen(pen)
        I=self.numPt
        J=0
        
        if self.single_piece_mode==True:
            if self.manualJ_mode==True:
                J=self.manualJ
            
            elif self.autoJ_mode==True:
                J = curve_fitting.findJ(self.vertices,self.angles,self.d_bar,self.center,self.Ea_criteria,self.Em_criteria)
                self.autoJ_value=J
            
            if self.manualJ_mode==True or self.autoJ_mode==True:
                self.a,self.b=curve_fitting.getCoefficients(J,self.vertices,self.center,self.angles)
                self.generalisedEllipseVertices,self.Ea,self.Em=curve_fitting.formGeneralizedEllipse(self.a,self.b,
                                                                                                     self.vertices,
                                                                                                     self.center,
                                                                                                     self.angles,
                                                                                                     self.d_bar)
     
                for i in range(I):
                    painter.drawLine(self.generalisedEllipseVertices[i][0]*300+self.width()/2.,self.generalisedEllipseVertices[i][1]*300+self.height()/2.,
                                     self.generalisedEllipseVertices[(i+1)%I][0]*300+self.width()/2.,self.generalisedEllipseVertices[(i+1)%I][1]*300+self.height()/2.)
                
        elif self.symmetry_mode==True:
            if self.manualJ_mode==True:
                J=self.manualJ

            elif self.autoJ_mode==True:
                J = curve_fitting.findJ(self.vertices_first_half,self.angles_first_half,self.d_bar,self.center_first_half,self.Ea_criteria,self.Em_criteria)
                self.autoJ_value=J

            if self.manualJ_mode==True or self.autoJ_mode==True:
                a_first_half, b_first_half = curve_fitting.getCoefficients_for_first_generalized_elliptic_segment(
                    self.vertices_first_half,
                    self.angles_first_half,
                    self.center_first_half, J)
                a_second_half, b_second_half = curve_fitting.getCoefficients_for_second_half_of_symmetrical_ellipse(
                    a_first_half, b_first_half)

                segmented_ellipse_vertices, Ea, Em = curve_fitting.form_vertices_of_segmented_ellipse(
                    self.vertices_first_half,
                    self.vertices_second_half,
                    self.center_first_half,
                    self.center_second_half,
                    self.angles_first_half,
                    self.angles_second_half,
                    self.d_bar, a_first_half,
                    b_first_half, a_second_half,
                    b_second_half)
                self.Ea = Ea
                self.Em = Em
                for i in range(self.numPt / 2):
                    painter.drawLine(segmented_ellipse_vertices[i][0] * 300 + self.width() / 2.,
                                     segmented_ellipse_vertices[i][1] * 300 + self.height() / 2.,
                                     segmented_ellipse_vertices[(i + 1) % self.numPt][0] * 300 + self.width() / 2.,
                                     segmented_ellipse_vertices[(i + 1) % self.numPt][1] * 300 + self.height() / 2.)
                second_half_color = QtGui.QColor(127, 0, 255)
                pen.setColor(second_half_color)
                painter.setPen(pen)
                for i in range(self.numPt / 2, self.numPt):
                    painter.drawLine(segmented_ellipse_vertices[i][0] * 300 + self.width() / 2.,
                                     segmented_ellipse_vertices[i][1] * 300 + self.height() / 2.,
                                     segmented_ellipse_vertices[(i + 1) % self.numPt][0] * 300 + self.width() / 2.,
                                     segmented_ellipse_vertices[(i + 1) % self.numPt][1] * 300 + self.height() / 2.)


        elif self.fragment_mode==True:
            if self.manualJ_mode==True:
                J=self.manualJ
                angles, vertices, center, self.start_index, self.end_index = curve_fitting.extract_fragment_data(self.vertices, self.angles, self.fragment_range)
                a,b=curve_fitting.getCoefficients_for_fragmented_ellipse(J,angles,vertices,center)
                fragment_vertices,Ea,Em = curve_fitting.form_vertices_of_fragment(a, b, vertices, center, angles, self.d_bar, self.start_index)
                self.Ea=Ea
                self.Em=Em
                for i in range(len(fragment_vertices)-1):
                    painter.drawLine(fragment_vertices[i][0]*300+self.width()/2.,fragment_vertices[i][1]*300+self.height()/2.,fragment_vertices[i+1][0]*300+self.width()/2.,fragment_vertices[i+1][1]*300+self.height()/2.)
                #maya_polygon_plane(self.generalisedEllipseVertices)

        elif self.composite_mode==True:
            if self.autoJ_mode==True:
                """
                # for the first segment
                J1 = curve_fitting.findJ(self.vertices_matrix[0], self.angles_matrix[0], self.d_bar, self.segment_center_list[0], self.Ea_criteria, self.Em_criteria)
                a,b=curve_fitting.getCoefficients_for_first_generalized_elliptic_segment(self.vertices_matrix[0], self.angles_matrix[0], self.segment_center_list[0],J1)
                fragment_vertices, Ea, Em = curve_fitting.form_vertices_of_fragment(a, b, self.vertices_matrix[0], self.angles_matrix[0], self.segment_center_list[0], self.d_bar, self.cut_points[0])
                if self.Ea < Ea:
                    self.Ea = Ea
                if self.Em < Em:
                    self.Em = Em
                """
                composite_vertices, Ea, Em = curve_fitting.composite_auto_mode(self.vertices_matrix, self.angles_matrix, self.segment_center_list, self.cut_points, self.d_bar, self.Ea_criteria, self.Em_criteria)
                for row in composite_vertices:
                    for i in range(len(row)-1):
                        painter.drawLine(row[i][0] * 300 + self.width() / 2.,
                                        row[i][1] * 300 + self.height() / 2.,
                                        row[i + 1][0] * 300 + self.width() / 2.,
                                        row[i + 1][1] * 300 + self.height() / 2.)


    def draw_originalEllipse(self,painter):
        penColor=QtCore.Qt.red   
        pen=QtGui.QPen()
        pen.setColor(penColor)
        pen.setWidthF(self.lineWidth)
        painter.setPen(pen)

        try:
            startPoint=QtCore.QPointF(self.vertices[0][0]*300+self.width()/2.,self.vertices[0][2]*self.height()/2.)
        except IndexError:
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.showMessage('Please choose a data file first')
        else:
            if self.fragment_mode==False and self.composite_mode==False:
                for i in range(self.numPt):
                    p1=QtCore.QPointF(self.vertices[i-1][0]*300+self.width()/2.,self.vertices[i-1][2]*300+self.height()/2.)
                    p2=QtCore.QPointF(self.vertices[i][0]*300+self.width()/2.,self.vertices[i][2]*300+self.height()/2.)
                    painter.drawLine(p1,p2)

                    if self.activateTangent == True:
                        t = QtGui.QVector2D(self.tangents[i][0],self.tangents[i][1]).normalized()*20.0
                        p3 = QtCore.QPointF(t.x()+p2.x(),t.y()+p2.y())
                        pen1 = QtGui.QPen()
                        pen1.setColor(QtCore.Qt.blue)
                        painter.setPen(pen1)
                        painter.drawLine(p2,p3)
                    if self.activateCurvature == True:
                        normal = self.normals[i]
                        p4 = QtCore.QPointF(normal.x()*self.curvatures[i]+p2.x(),normal.y()*self.curvatures[i]+p2.y())
                        pen2 = QtGui.QPen()
                        pen2.setColor(QtCore.Qt.green)
                        painter.setPen(pen2)
                        painter.drawLine(p2, p4)

                    painter.setPen(pen)


                if self.activateCutPoint == True:
                    od = curve_fitting.sortCurvature(self.curvatures)
                    # show first 5 cut point candidates based on curvatures on original curve
                    for i in range(20):
                        index = od[-i][0]
                        p = self.vertices[index]
                        painter.drawText (p[0]*300+self.width()/2., p[2]*300+self.height()/2., str(index))

            elif self.fragment_mode==True:
                if self.start_index<self.end_index:
                    for i in range(self.start_index+1,self.end_index+1):   
                        p1=QtCore.QPointF(self.vertices[i-1][0]*300+self.width()/2.,self.vertices[i-1][2]*300+self.height()/2.)
                        p2=QtCore.QPointF(self.vertices[i][0]*300+self.width()/2.,self.vertices[i][2]*300+self.height()/2.)
                        painter.drawLine(p1,p2) 
                else:        
                    for i in range(self.start_index+1,self.numPt):   
                        p1=QtCore.QPointF(self.vertices[i-1][0]*300+self.width()/2.,self.vertices[i-1][2]*300+self.height()/2.)
                        p2=QtCore.QPointF(self.vertices[i][0]*300+self.width()/2.,self.vertices[i][2]*300+self.height()/2.)
                        painter.drawLine(p1,p2)   
                    for i in range(self.end_index+1):   
                        p1=QtCore.QPointF(self.vertices[i-1][0]*300+self.width()/2.,self.vertices[i-1][2]*300+self.height()/2.)
                        p2=QtCore.QPointF(self.vertices[i][0]*300+self.width()/2.,self.vertices[i][2]*300+self.height()/2.)
                        painter.drawLine(p1,p2)

            elif self.composite_mode==True:
                for row in self.vertices_matrix:
                    pen3 = QtGui.QPen()
                    color = QtGui.QColor(random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
                    pen3.setColor(color)
                    painter.setPen(pen3)
                    for i in range(len(row)-1):
                        p1 = QtCore.QPointF(row[i][0] * 300 + self.width() / 2.,row[i][2] * 300 + self.height() / 2.)
                        p2 = QtCore.QPointF(row[i+1][0] * 300 + self.width() / 2.,row[i+1][2] * 300 + self.height() / 2.)
                        painter.drawLine(p1, p2)

                painter.setPen(pen)


    def draw_standardEllipse(self,painter):
        penColor=QtCore.Qt.blue        
        pen=QtGui.QPen()
        pen.setColor(penColor)
        pen.setWidthF(self.lineWidth)
        painter.setPen(pen)
        
        # calculate the major axis and minor axis
        a0u=0.0
        a0b=0.0
        b0u=0.0
        b0b=0.0
        try:
            for i in range(self.numPt):
                angle=self.angles[i]
                a0u=a0u+(self.vertices[i][0]-self.center.x())*math.sin(angle)
                a0b=a0b+math.sin(angle)*math.sin(angle)
                b0u=b0u+(self.vertices[i][2]-self.center.y())*math.cos(angle)
                b0b=b0b+math.cos(angle)*math.cos(angle)
                
        except IndexError:
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.showMessage('Please choose a data file first')
        else:
            width=a0u/a0b
            height=b0u/b0b
            painter.drawEllipse(self.center+QtCore.QPointF(self.width()/2., self.height()/2.), width*300, height*300)


    def getEm(self):
        return self.Em
        
        
    def getEa(self):
        return self.Ea


def maya_polygon_plane(generalisedEllipseVertices):
    """
    test the plane in Maya
    """
    width = 10.0
    length = 10.0
    face_count = 1
    vertex_count = len(generalisedEllipseVertices)
    # Create vertex positions
    vertices = OpenMaya.MFloatPointArray()
    for v in generalisedEllipseVertices:
        vertices.append(OpenMaya.MFloatPoint(v[0]*300, 0.0, v[1]*300))

    # Vertex count for this polygon face
    face_vertexes = OpenMaya.MIntArray()
    face_vertexes.append(vertex_count)

    # Vertex indexes for this polygon face
    vertex_indexes = OpenMaya.MIntArray()
    vertex_indexes.copy([i for i in range(vertex_count)])

    # Create mesh
    mesh_object = OpenMaya.MObject()
    mesh = OpenMaya.MFnMesh()
    mesh_object = mesh.create(vertices, face_vertexes, vertex_indexes)
    mesh.updateSurface()
    # Assign default shading
    cmds.sets(mesh.name(), edit=True, forceElement="initialShadingGroup")
    
    
if __name__=="__main__":
    # Check to see if the UI already exists and if so, delete
    if cmds.window("generalizedEllipseWin",exists=True):
        cmds.deleteUI("generalizedEllipseWin",wnd=True)
        
    w=CurveFittingWindowUI()
    w.show()  
    #w.raise_() 

