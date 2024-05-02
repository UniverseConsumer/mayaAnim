import unreal 
import os

def ImportSkeletalMesh(meshPath):

    importTask = CreateImportTask(meshPath)

    importOptions = unreal.FbxImportUI()
    importOptions.import_mesh = True
    importOptions.import_as_skeletal = True
    importOptions.skeletal_mesh_import_data.set_editor_property('import_morph.targets', True)
    importOptions.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', True)

    importTask.options = importOptions

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])
    return importTask.get_objects()[0]

def CreateImportTask(meshPath):
    importTask = unreal.AssetImportTask()
    importTask.filename = meshPath
    assetName = os.path.basename(os.path.abspath(meshPath)).split(".")[0]
    importTask.destination_path = '/game/' + assetName
    importTask.automated = True # do not popup the inport options
    importTask.save = True
    importTask.replace_existing = True
    return importTask

def importAnim(mesh: unreal.SkeletalMesh, animPath):
    importTask = CreateImportTask(animPath)
    meshDir = os.path.dirname(mesh.get_path_name())
    importTask.destination_path = meshDir + "/animations"

    importOptions = unreal.FbxImportUI()
    importOptions.import_mesh = False
    importOptions.import_as_skeletal = True
    importOptions.import_animations = True

    importOptions.set_editor_property('automated_import_should_detect_type', False)
    importOptions.set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    importOptions.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_ANIMATION)

    importTask.options = importOptions

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])

def ImportMeshAndAnims(meshpath, animDir):
    mesh = ImportSkeletalMesh(meshpath)
    for fileName in os.listdir(animDir):
        if ".fbx" in fileName:
            animPath = os.path.join(animDir, fileName)
            importAnim(mesh, animPath)

ImportMeshAndAnims("EnterMeshDirHere", "EnterAnimDirHere")