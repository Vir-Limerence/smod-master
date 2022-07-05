import os
import sys
import importlib


class plugins:
    pluginTree = list()
    modules = dict()

    def __init__(self, path):
        self.path = path

    def crawler(self):
        for top, dirs, files in os.walk(self.path):
            for sub in files:
                if sub.endswith('.py'):
                    self.pluginTree.append(os.path.join(top, sub).replace(self.path, '').replace('.py', '').split('/'))

    def load(self):
        for plugin in self.pluginTree:
            name = plugin[-1]
            item = '/'.join(plugin)
            """importlib.invalidate_caches()
            ip_module = importlib.import_module(self.path + item + '.py')
            ip_module_cls = getattr(ip_module, 'Module')
            cls_obj = ip_module_cls()
            """
            spec = importlib.util.spec_from_file_location(name, self.path + item + '.py')
            the_api = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(the_api)
            self.modules.update({item:the_api.Module()})
            #self.modules.update({item:importlib.machinery.SourceFileLoader(name, self.path + item + '.py').exec_module()})
            
