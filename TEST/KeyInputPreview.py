import bpy


class Test_Ops2(bpy.types.Operator):
    bl_label = '测试执行顺序'
    bl_idname = 'a_test.test_ops2'
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        print("INVOKE")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type != "MOUSEMOVE":
            print(f"按键:{event.type},状态:{event.value}")

        if event.type == "LEFTMOUSE":
            return {"PASS_THROUGH"}

        if event.type == "ESC":
            return {"FINISHED"}

        return {"RUNNING_MODAL"}


bpy.utils.register_class(Test_Ops2)
