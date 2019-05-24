# cross_section_cmd.py
# Author: Xiaosong Yang, Ouwen Li
# Email: leeowen988@gmail.com
# Version: 2.0
# Autodesk Maya Command template API 2.0
# Copyright (C) 2019 Xiaosong Yang
#-------------------------------------------------
import maya.api.OpenMaya as om

def maya_useNewAPI():
    pass

##############################################################################
##
## Command class implementation
##
##############################################################################
class CrossSectionExtractCmd(om.MPxCommand):
    kPluginName='crossSectionExtract'
    def __init__(self):
        om.MPxCommand.__init__(self)
        self.mesh_name=''
        self.bone_name=''    
        self.u_parameter=0.0    #default value
        
    @staticmethod
    def creator():
        return CrossSectionExtractCmd()
        
        
    @staticmethod
    def syntaxCreator():
        syntax=om.MSyntax()
        syntax.addFlag('-mu','-myUparameter',om.MSyntax.kDouble)
        syntax.addFlag('-mmn','-myMeshName',om.MSyntax.kString)
        syntax.addFlag('-mbn','-myBoneName',om.MSyntax.kString)
        return syntax
        
        
    def doIt(self,args):
        self.parseArguments(args)
                
        #DO THE WORK
        self.redoIt()


    def parseArguments(self, args):
        argData=om.MArgDatabase(self.syntax(),args)
        if argData.isFlagSet('-mu'):
            self.u = argData.flagArgumentDouble( '-mu', 0 )
        if argData.isFlagSet('-mmn'):
            self.mesh_name = argData.flagArgumentString( '-mmn', 0 )
        if argData.isFlagSet('-mbn'):
            self.bone_name = argData.flagArgumentString( '-mbn', 0 )  
                                      
        
    def redoIt(self):      
        # WHEN NO MESH IS SPECIFIED IN THE COMMAND, GET THE FIRST SELECTED MESH FROM THE SELECTION LIST:
        if (self.mesh_name == "") or (self.bone_name == ""):
            sList = om.MGlobal.getActiveSelectionList()
                      
            iter=om.MItSelectionList (sList, om.MFn.kMesh)
            i=0
            
            while( not iter.isDone()): 
                # RETRIEVE THE MESH
                meshDagPath = iter.getDagPath()
                i+=1
                iter.next()
          
            if i==0: 
                raise ValueError("No mesh or mesh transform specified!")
            elif i>1:
                raise ValueError("Multiple meshes or mesh transforms specified!")
            iter.reset()
            iter=om.MItSelectionList (sList, om.MFn.kJoint)
            i=0
            while not iter.isDone(): 
                #RETRIEVE THE JOINT
                meshDagPath = iter.getDagPath()
                i+=1
                iter.next()
                
            if i==0: 
                raise ValueError("No bone or bone transform specified!")
            elif i>1:
                raise ValueError("Multiple bones or bone transforms specified!")
            
                               

def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.registerCommand(CrossSectionExtractCmd.kPluginName, CrossSectionExtractCmd.creator, CrossSectionExtractCmd.syntaxCreator)
    except:
        raise
        
        
def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(CrossSectionExtractCmd.kPluginName)
    except:
        raise



        
