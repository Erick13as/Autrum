using Gtk

# convert glade file using Gtk Builder()

glade = GtkBuilder(filename = "Autrum.glade")

# assign variables

window = glade["window"]
label = glade["label"]
button = glade["button"]

# launch GUI

showall(window)

# set button callback

id = signal_connect(button, "button-press-event") do widget, event
    if get_gtk_property(label, :label, String) == "Hi"
        GAccessor.text(label, "Prueba")
    else
        GAccessor.text(label, "Hi")
    end
end