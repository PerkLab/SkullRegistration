import os
import unittest
import vtk, qt, ctk, slicer
from Guidelet import GuideletLoadable, GuideletWidget, GuideletLogic, GuideletTest
from Guidelet import Guidelet
import logging

#--------------------------------------------------------------------------------------------------
# USRegistration
#--------------------------------------------------------------------------------------------------
class USRegistration(GuideletLoadable):

  def __init__(self, parent):
    GuideletLoadable.__init__(self, parent)
    self.parent.title = "US Registration"
    self.parent.categories = ["Registration.US Skull"]
    self.parent.dependencies = ["Sequences"]
    self.parent.contributors = ["Mark Asselin (PerkLab, Queen's University & ACMIT GmbH)"]
    self.parent.helpText = """
This module implments a clinically feasible interface for performing an intra-operative skull
registration using tracked ultrasound.
"""
    self.parent.acknowledgementText = """
This file was originally developed by Mark Asselin at ACMIT GmBH.
"""


#--------------------------------------------------------------------------------------------------
# USRegistrationWidget
#--------------------------------------------------------------------------------------------------
class USRegistrationWidget(GuideletWidget):

  def __init__(self, parent=None):
    GuideletWidget.__init__(self, parent)


  def setup(self):
    logging.debug('USRegistrationWidget.setup(self)')
    GuideletWidget.setup(self)


  def addLauncherWidgets(self):
    logging.debug('USRegistrationWidget.addLauncherWidgets(self)')
    GuideletWidget.addLauncherWidgets(self)


  def onConfigurationChanged(self, selectedConfigurationName):
    logging.debug('USRegistrationWidget.onConfigurationChanged(self, selectedConfigurationName)')
    GuideletWidget.onConfigurationChanged(self, selectedConfigurationName)


  def createGuideletInstance(self):
    logging.debug('USRegistrationWidget.createGuideletInstance(self)')
    return USRegistrationGuidelet(None, self.guideletLogic, self.selectedConfigurationName)


  def createGuideletLogic(self):
    logging.debug('USRegistrationWidget.createGuideletLogic(self)')
    return USRegistrationLogic()


#--------------------------------------------------------------------------------------------------
# USRegistrationLogic 
#--------------------------------------------------------------------------------------------------
class USRegistrationLogic(GuideletLogic):

  def __init__(self, parent=None):
    GuideletLogic.__init__(self, parent)

  def addValuesToDefaultConfiguration(self):
    logging.debug('USRegistrationLogic.addValuesToDefaultConfiguration(self)')
    GuideletLogic.addValuesToDefaultConfiguration(self)
    moduleDir = os.path.dirname(slicer.modules.usregistration.path)
    defaultSavePathOfUSRegistration = os.path.join(moduleDir, 'SavedScenes')
    settingList = {'StyleSheet' : moduleDir + '/Resources/StyleSheets/USRegistrationStyle.qss',
                   'RecordingFilenamePrefix' : 'USRegistrationRecording-',
                   'SavedScenesDirectory': defaultSavePathOfUSRegistration,
                   }
    self.updateSettings(settingList, 'Default')


#--------------------------------------------------------------------------------------------------
# USRegistrationTest
#--------------------------------------------------------------------------------------------------
class USRegistrationTest(GuideletTest):

  def runTest(self):
    logging.debug('USRegistrationTest.runTest(self)')
    GuideletTest.runTest(self)
    #self.test_USRegistration1() #add applet specific tests here


#--------------------------------------------------------------------------------------------------
# USRegistrationGuidelet
#--------------------------------------------------------------------------------------------------
class USRegistrationGuidelet(Guidelet):

  USRegistration_REFERENCE_WATCHDOG = 0
  USRegistration_PROBE_WATCHDOG = 1
  USRegistration_STYLUS_WATCHDOG = 1

  def __init__(self, parent, logic, configurationName='Default'):

    # init guidelet
    Guidelet.__init__(self, parent, logic, configurationName)

    # module intrinsics
    self.logic.addValuesToDefaultConfiguration()
    self.modulePath = os.path.dirname(slicer.modules.usregistration.path)
    self.moduleTransformsPath = os.path.join(self.modulePath, 'Resources/Transforms')
    self.moduleModelsPath = os.path.join(self.modulePath, 'Resources/Models')
    self.moduleIconsPath = os.path.join(self.modulePath, 'Resources/Icons')

    self.referenceInView = False
    self.probeInView = False
    self.stylusInView = False
    
    # set up main frame
    self.sliceletDockWidget.setObjectName('USRegistration')
    self.sliceletDockWidget.setWindowTitle('Skull US Registration')
    self.mainWindow.setWindowTitle('Skull US Registration')
    self.mainWindow.windowIcon = qt.QIcon(os.path.join(self.moduleIconsPath, 'USRegistration.png'))
    
    # hide slicer status bar
    slicer.util.mainWindow().statusBar().hide()
    
    # setup
    self.setupScene()

    # tool visibility icons
    self.setupToolWatchdog()
  

  def __del__(self):
      self.preCleanup()


  def preCleanup(self):
    logging.debug('USRegistrationGuidelet.preCleanup')
    Guidelet.preCleanup(self)


  def createFeaturePanels(self):
    logging.debug('USRegistrationGuidelet.createFeaturePanels')

    moduleDirectoryPath = slicer.modules.usregistration.path.replace('USRegistration.py', '')
    self.uiWidget = slicer.util.loadUI(moduleDirectoryPath + 'Resources/UI/USRegistration.ui')
    self.sliceletPanelLayout.addWidget(self.uiWidget)
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)

    featurePanelList = [
      self.ui.captureCollapsibleButton,
      self.ui.segmentCollapsibleButton,
      self.ui.registerCollapsibleButton,
      self.ui.verifyCollapsibleButton,
      ]

    featurePanelList[len(featurePanelList):] = Guidelet.createFeaturePanels(self)

    self.sliceletPanelLayout.addItem(qt.QSpacerItem(20, 40, qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding))

    return featurePanelList

  def setupScene(self):
    logging.debug('USRegistrationGuidelet.setupScene')

    Guidelet.setupScene(self)

    self.setupTransforms()
    self.setupModels()
    self.setupTransformTree()

    # hide slice view annotations (patient name, scale, color bar, etc.) as they
    # decrease reslicing performance by 20%-100%
    logging.debug('USRegistrationGuidelet: Hide slice view annotations')
    import DataProbe
    dataProbeUtil=DataProbe.DataProbeLib.DataProbeUtil()
    dataProbeParameterNode=dataProbeUtil.getParameterNode()
    dataProbeParameterNode.SetParameter('showSliceViewAnnotations', '0')


  def setupTransforms(self):
    logging.debug('USRegistrationGuidelet.setupTransforms')

    # ImageToProbe
    self.imageToProbe = slicer.util.getFirstNodeByName(
      'ImageToProbe', className='vtkMRMLLinearTransformNode')
    if not self.imageToProbe:
      imageToProbeFilePath = os.path.join(self.moduleTransformsPath, 'ImageToProbe.h5')
      self.imageToProbe = slicer.util.loadTransform(imageToProbeFilePath)
      if self.imageToProbe is None:
        logging.error('Could not read ImageToProbe transform')
      else:
        self.imageToProbe.SetName("ImageToProbe")
        slicer.mrmlScene.AddNode(self.imageToProbe)

    # StylusTipToStylus
    self.stylusTipToStylus = slicer.util.getFirstNodeByName(
      'StylusTipToStylus', className='vtkMRMLLinearTransformNode')
    if not self.stylusTipToStylus:
      stylusTipToStylusFilePath = os.path.join(self.moduleTransformsPath, 'StylusTipToStylus.h5')
      self.stylusTipToStylus = slicer.util.loadTransform(stylusTipToStylusFilePath)
      if self.stylusTipToStylus is None:
        logging.error('Could not read StylusTipToStylus transform')
      else:
        self.stylusTipToStylus.SetName("StylusTipToStylus")
        slicer.mrmlScene.AddNode(self.stylusTipToStylus)

    # create transforms that will be updated through OpenIGTLink
    # ProbeToReference
    self.probeToReference = slicer.util.getFirstNodeByName('ProbeToReference', className='vtkMRMLLinearTransformNode')
    if not self.probeToReference:
      self.probeToReference = slicer.vtkMRMLLinearTransformNode()
      self.probeToReference.SetName('ProbeToReference')
      slicer.mrmlScene.AddNode(self.probeToReference)

    # StylusToReference
    self.stylusToReference = slicer.util.getFirstNodeByName('StylusToReference', className='vtkMRMLLinearTransformNode')
    if not self.stylusToReference:
      self.stylusToReference = slicer.vtkMRMLLinearTransformNode()
      self.stylusToReference.SetName('StylusToReference')
      slicer.mrmlScene.AddNode(self.stylusToReference)

    # ReferenceToTracker (for watchdog)
    self.referenceToTracker = slicer.util.getFirstNodeByName('ReferenceToTracker', className='vtkMRMLLinearTransformNode')
    if not self.referenceToTracker:
      self.referenceToTracker = slicer.vtkMRMLLinearTransformNode()
      self.referenceToTracker.SetName('ReferenceToTracker')
      slicer.mrmlScene.AddNode(self.referenceToTracker)

    # ProbeToTracker (for watchdog)
    self.probeToTracker = slicer.util.getFirstNodeByName('ProbeToTracker', className='vtkMRMLLinearTransformNode')
    if not self.probeToTracker:
      self.probeToTracker = slicer.vtkMRMLLinearTransformNode()
      self.probeToTracker.SetName('ProbeToTracker')
      slicer.mrmlScene.AddNode(self.probeToTracker)

    # StylusToTracker (for watchdog)
    self.stylusToTracker = slicer.util.getFirstNodeByName('StylusToTracker', className='vtkMRMLLinearTransformNode')
    if not self.stylusToTracker:
      self.stylusToTracker = slicer.vtkMRMLLinearTransformNode()
      self.stylusToTracker.SetName('StylusToTracker')
      slicer.mrmlScene.AddNode(self.stylusToTracker)


  def setupModels(self):
    logging.debug('USRegistrationGuidelet.setupModels')

    # UsProbe model
    self.probeModel = slicer.util.getFirstNodeByName('probeModel','vtkMRMLModelNode')
    if not self.probeModel:
      probeModelFilePath = os.path.join(self.moduleModelsPath, 'TelemedL12.stl')
      self.probeModel = slicer.util.loadModel(probeModelFilePath)
      if self.probeModel is None:
        logging.debug('UsProbe model not found ({0})'.format(probeModelFilePath))
      else:
        logging.debug('Loaded UsProbe model: {0}'.format(probeModelFilePath))
        self.probeModel.GetDisplayNode().SetColor(1.0, 1.0, 1.0)
        self.probeModel.SetName('ProbeModel')
      

  def setupTransformTree(self):
    logging.debug('USRegistrationGuidelet.setupTransformTree')
    # transforms
    self.imageToProbe.SetAndObserveTransformNodeID(self.probeToReference.GetID())
    self.stylusTipToStylus.SetAndObserveTransformNodeID(self.stylusToReference.GetID())

    # models
    self.probeModel.SetAndObserveTransformNodeID(self.probeToReference.GetID())

  
  def setupToolWatchdog(self):
    logging.debug('USRegistrationGuidelet.setupToolVisibilityIcons')
    self.ui.referenceVisButton.setIcon(qt.QIcon(os.path.join(self.moduleIconsPath, 'TrackingStatusRed.svg')))
    self.ui.referenceVisLabel.setStyleSheet("color: red")

    self.ui.probeVisButton.setIcon(qt.QIcon(os.path.join(self.moduleIconsPath, 'TrackingStatusRed.svg')))
    self.ui.probeVisLabel.setStyleSheet("color: red")

    self.ui.stylusVisButton.setIcon(qt.QIcon(os.path.join(self.moduleIconsPath, 'TrackingStatusRed.svg')))
    self.ui.stylusVisLabel.setStyleSheet("color: red")

    self.watchdog = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLWatchdogNode')
    if self.watchdog is None:
      self.watchdog = slicer.vtkMRMLWatchdogNode()
      self.watchdog.SetName('TrackingWatchdog')
      slicer.mrmlScene.AddNode(self.watchdog)
    else:
      self.watchdog.RemoveAllDisplayNodeIDs()

    self.watchdog.AddWatchedNode(self.referenceToTracker, 'Reference', 0)
    self.watchdog.AddWatchedNode(self.probeToTracker, 'Probe', 0)
    self.watchdog.AddWatchedNode(self.stylusToTracker, 'Stylus', 0)

    watchdogDisplayNode = slicer.vtkMRMLWatchdogDisplayNode()
    watchdogDisplayNode.SetName('TrackingWatchdogDisplay')
    slicer.mrmlScene.AddNode(watchdogDisplayNode)
    watchdogDisplayNode.AddViewNodeID('vtkMRMLViewNode')
    self.watchdog.SetAndObserveDisplayNodeID(watchdogDisplayNode.GetID())

    qt.QTimer.singleShot(200, lambda: self.watchdog.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateToolVisibility))


  def setupConnections(self):
    logging.debug('USRegistrationGuidelet.setupConnections')
    Guidelet.setupConnections(self)

    # panels
    self.ui.captureCollapsibleButton.connect('toggled(bool)', self.onCapturePanelToggled)
    self.ui.segmentCollapsibleButton.connect('toggled(bool)', self.onSegmentPanelToggled)
    self.ui.registerCollapsibleButton.connect('toggled(bool)', self.onRegisterPanelToggled)
    self.ui.verifyCollapsibleButton.connect('toggled(bool)', self.onVerifyPanelToggled)

    # capture panel

    # segment panel

    # register panel

    # verify panel


  def disconnect(self):
    logging.debug('USRegistrationGuidelet.disconnect')
    Guidelet.disconnect(self)

     # panels
    self.ui.captureCollapsibleButton.disconnect('toggled(bool)', self.onCapturePanelToggled)
    self.ui.segmentCollapsibleButton.disconnect('toggled(bool)', self.onSegmentPanelToggled)
    self.ui.registerCollapsibleButton.disconnect('toggled(bool)', self.onRegisterPanelToggled)
    self.ui.verifyCollapsibleButton.disconnect('toggled(bool)', self.onVerifyPanelToggled)

    # capture panel

    # segment panel

    # register panel

    # verify panel
 
 
#--------------------------------------------------------------------------------------------------
# callbacks: panel toggled

  def onCapturePanelToggled(self, toggled):
    logging.debug('USRegistrationGuidelet.onCalibrationPanelToggled')
    if toggled:
      self.selectView(self.VIEW_3D)


  def onSegmentPanelToggled(self, toggled):
    logging.debug('USRegistrationGuidelet.onSamplingPanelToggled')
    if toggled:
      self.selectView(self.VIEW_4UP)


  def onRegisterPanelToggled(self, toggled):
    logging.debug('USRegistrationGuidelet.onDataPanelToggled')
    if toggled:
      self.selectView(self.VIEW_3D)


  def onVerifyPanelToggled(self, toggled):
    logging.debug('USRegistrationGuidelet.onDataPanelToggled')
    if toggled:
      self.selectView(self.VIEW_4UP)


#--------------------------------------------------------------------------------------------------
# callbacks: capture panel


#--------------------------------------------------------------------------------------------------
# callbacks: segment panel



#--------------------------------------------------------------------------------------------------
# callbacks: register panel


#--------------------------------------------------------------------------------------------------
# callbacks: verify panel


#--------------------------------------------------------------------------------------------------
# tool visibility logic

  def updateToolVisibility(self, observer, eventId):
    
    if self.watchdog is not None:

      if self.watchdog.GetWatchedNodeUpToDate(self.USRegistration_REFERENCE_WATCHDOG):
        self.referenceInView = True
        self.ui.referenceVisButton.setIcon(qt.QIcon(os.path.join(self.moduleIconsPath, 'TrackingStatusGreen.svg')))
        self.ui.referenceVisLabel.setStyleSheet("color: #0B9A4F")
      else:
        self.referenceInView = False
        self.ui.referenceVisButton.setIcon(qt.QIcon(os.path.join(self.moduleIconsPath, 'TrackingStatusRed.svg')))
        self.ui.referenceVisLabel.setStyleSheet("color: red")

      if self.watchdog.GetWatchedNodeUpToDate(self.USRegistration_PROBE_WATCHDOG):
        self.probeInView = True
        self.ui.probeVisButton.setIcon(qt.QIcon(os.path.join(self.moduleIconsPath, 'TrackingStatusGreen.svg')))
        self.ui.probeVisLabel.setStyleSheet("color: #0B9A4F")
      else:
        self.probeInView = False
        self.ui.probeVisButton.setIcon(qt.QIcon(os.path.join(self.moduleIconsPath, 'TrackingStatusRed.svg')))
        self.ui.probeVisLabel.setStyleSheet("color: red")


      if self.watchdog.GetWatchedNodeUpToDate(self.USRegistration_STYLUS_WATCHDOG):
        self.stylusInView = True
        self.ui.stylusVisButton.setIcon(qt.QIcon(os.path.join(self.moduleIconsPath, 'TrackingStatusGreen.svg')))
        self.ui.stylusVisLabel.setStyleSheet("color: #0B9A4F")
      else:
        self.stylusInView = False
        self.ui.stylusVisButton.setIcon(qt.QIcon(os.path.join(self.moduleIconsPath, 'TrackingStatusRed.svg')))
        self.ui.stylusVisLabel.setStyleSheet("color: red")
  
    else:
      self.referenceInView = False
      self.probeInView = False
      self.stylusInView = False


#--------------------------------------------------------------------------------------------------
# get stylesheet

  def getStylesheet(self):
    return self.loadStyleSheet()


#--------------------------------------------------------------------------------------------------
# dialogs

class YesNoDialog(qt.QDialog):

  def __init__(self, parent=None, stylesheet=None):
    qt.QDialog.__init__(self, parent)
    self.setupUi()
    self.yesButton.connect('clicked(bool)', self.onYesButtonClicked)
    self.noButton.connect('clicked(bool)', self.onNoButtonClicked)
    self.setStyleSheet(stylesheet)


  def setupUi(self):
    logging.debug('YesNoDialog.setupUi')
    layout = qt.QVBoxLayout()
    self.infoLabel = qt.QLabel('')
    layout.addWidget(self.infoLabel)
    self.buttonBox = qt.QDialogButtonBox()
    self.yesButton = self.buttonBox.addButton(qt.QDialogButtonBox.Yes)
    self.noButton = self.buttonBox.addButton(qt.QDialogButtonBox.No)
    self.yesButton.setStyleSheet('padding: 0px 40px 0px 40px;')
    self.noButton.setStyleSheet('padding: 0px 40px 0px 40px;')
    layout.addWidget(self.buttonBox)
    self.setLayout(layout)
    self.setWindowModality(qt.Qt.ApplicationModal)
    
    
  def setInfoMessage(self, message):
    logging.debug('YesNoDialog.setInfoMessage')
    self.infoLabel.setText(message)


  def onYesButtonClicked(self):
    logging.debug('YesNoDialog.onYesButtonClicked')
    self.done(1)


  def onNoButtonClicked(self):
    logging.debug('YesNoDialog.onNoButtonClicked')
    self.done(0)


  def show(self):
    logging.debug('YesNoDialog.show')
    return self.exec_()


class OkDialog(qt.QDialog):

  def __init__(self, parent=None, stylesheet=None):
    qt.QDialog.__init__(self, parent)
    self.setupUi()
    self.okButton.connect('clicked(bool)', self.onOkButtonClicked)
    self.setStyleSheet(stylesheet)


  def setupUi(self):
    logging.debug('OkDialog.setupUi')
    layout = qt.QVBoxLayout()
    self.infoLabel = qt.QLabel('')
    layout.addWidget(self.infoLabel)
    self.buttonBox = qt.QDialogButtonBox()
    self.okButton = self.buttonBox.addButton(qt.QDialogButtonBox.Ok)
    self.okButton.setStyleSheet('padding: 0px 40px 0px 40px;')
    layout.addWidget(self.buttonBox)
    self.setLayout(layout)
    self.setWindowModality(qt.Qt.ApplicationModal)
    
    
  def setInfoMessage(self, message):
    logging.debug('OkDialog.setInfoMessage')
    self.infoLabel.setText(message)


  def onOkButtonClicked(self):
    logging.debug('OkDialog.onOkButtonClicked')
    self.done(0)


  def show(self):
    logging.debug('OkDialog.show')
    self.exec_()