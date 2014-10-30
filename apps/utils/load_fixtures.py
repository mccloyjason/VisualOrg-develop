import importlib


def load_fixtures(name, put_on=None):
    module_name = "visualorg.fixture_scripts.{}".format(name)
    module = importlib.import_module(module_name)
    if hasattr(module, 'models'):
        for model in module.models:
            model.objects.all().delete()
    results = module.load()
    if put_on:
        for key, value in results.items():
            setattr(put_on, key, value)
