from importlib.metadata import entry_points

eps = entry_points()
plugin_entr_points = eps.select(group="zk_rag_plugins")
for ep in plugin_entr_points:
    print(ep)
    # plugin_class = ep.load()  # Dynamically import and load the object
    # plugin = plugin_class()
    # print(plugin.run("Bandura"))
    # print(plugin.descriptor)
