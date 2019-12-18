import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# AutomaticSurfacePointPlacement
#

class AutomaticSurfacePointPlacement(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Automatic Point Placement" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Registration.US Skull"]
    self.parent.dependencies = []
    self.parent.contributors = ["Abigael Schonewille, Tamas Ungi & Mark Asselin (PerkLab, Queen's University)"]
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# AutomaticSurfacePointPlacementWidget
#

class AutomaticSurfacePointPlacementWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/AutomaticSurfacePointPlacement.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    self.ui.inputSequence.setMRMLScene(slicer.mrmlScene)
    self.ui.outputMarkups.setMRMLScene(slicer.mrmlScene)

    # connections
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.ui.inputSequence.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.ui.outputMarkups.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.ui.applyButton.enabled = self.ui.inputSequence.currentNode() and self.ui.outputMarkups.currentNode()

  def onApplyButton(self):
    logic = AutomaticSurfacePointPlacementLogic()
    segmentationThreshold = self.ui.segmentationThreshold.value
    minimumDistance = self.ui.minimumDistance.value
    deepLearningModelPath = self.ui.deepLearningModel.currentPath
    print(deepLearningModelPath)
    logic.run(self.ui.inputSequence.currentNode(), self.ui.outputMarkups.currentNode(), segmentationThreshold, minimumDistance, deepLearningModelPath)

#
# AutomaticSurfacePointPlacementLogic
#

class AutomaticSurfacePointPlacementLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def isValidInputOutputData(self, inputSequence, outputMarkups, segmentationThreshold, minimumDistance, deepLearningModelPath):
    """
    Validate the inputs
    """
    import os.path

    if minimumDistance < 0:
      logging.debug('isValidInputOutputData failed: minimum point distance provided was negative')
      return False
    if segmentationThreshold < 0 or segmentationThreshold > 1:
      logging.debug('isValidInputOutputData failed: segmentation threshold provided was not within the range 0-1')
      return False
    if not inputSequence:
      logging.debug('isValidInputOutputData failed: no input sequence node defined')
      return False
    if not outputMarkups:
      logging.debug('isValidInputOutputData failed: no output markups node defined')
      return False
    if not os.path.isfile(deepLearningModelPath):
      logging.debug('isValidInputOutputData failed: path provided is not a file')
      return False
    return True

  def loadModel(self, deepLearningModelPath):
    #from keras import models.load_model

    try:
      model = models.load_model(deepLearningModelPath)
    except:
      logging.debug('isValidInputOutputData failed: invalid deep learning model provided')
      return False
    return model


  def run(self, inputSequence, outputMarkups, segmentationThreshold, minimumDistance, deepLearningModelPath):
    """
    Run the actual algorithm to place points with a min distance
    """

    if not self.isValidInputOutputData(inputSequence, outputMarkups, segmentationThreshold, minimumDistance, deepLearningModelPath):
      slicer.util.errorDisplay('Inputs provided are not valid.')
      return False

    if not self.loadModel(deepLearningModelPath):
      slicer.util.errorDisplay('Deep learning model provided is not valid.')
      return False

    logging.info('Processing started')


    logging.info('Processing completed')

    return True


class AutomaticSurfacePointPlacementTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_AutomaticSurfacePointPlacement1()

  def test_AutomaticSurfacePointPlacement1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = AutomaticSurfacePointPlacementLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
