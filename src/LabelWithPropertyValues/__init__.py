#### Custom Viewport Overlay ####
# Description of your Python-based viewport layer.

from ovito.data import DataCollection, DataObject, Particles
from ovito.qt_compat import QtCore, QtGui
from ovito.traits import ColorTrait, PropertyReference
from ovito.vis import ViewportOverlayInterface
from traits.api import Bool, Float, Range


class LabelWithPropertyValues(ViewportOverlayInterface):
    
    input_property = PropertyReference(
        container=DataObject.Ref(Particles),
        default_value='Particle Identifier',
        mode=PropertyReference.Mode.PropertiesAndComponents,
        label="Particle Property", ovito_group = "General settings"
    )   
    use_only_selected = Bool(False, label="Label only selected particles", ovito_group = "General settings")

    group1 = "Visual elements"
    font_size = Float(0.05, label="Font size", ovito_group=group1)
    text_color = ColorTrait((0.0, 0.0, 0.0), label="Text color", ovito_group=group1)
    outline_width = Range(low=0, high=None, value=0, label="Outline width", ovito_group=group1)
    outline_color = ColorTrait((1.0, 1.0, 1.0), label="Outline color", ovito_group=group1)    

    group2 = "Positioning (in relation to screen radius)" 
    px = Range(low=-1., high=1., value=0.0, label="X-offset", ovito_unit="percent", ovito_group=group2)
    py = Range(low=-1., high=1., value=0.0, label="Y-offset", ovito_unit="percent", ovito_group=group2)  
   
    def render(self, canvas: ViewportOverlayInterface.Canvas, data: DataCollection, **kwargs):

        prop = data.particles[self.input_property]
        if prop is not None:    
            # Project center of the particle to screen space.
            positions = data.particles.positions
          
            for i in range(data.particles.count):
                if self.use_only_selected and data.particles.selection[i] == 0:
                    continue
                radius = 0.0
                if 'Radius' in data.particles:
                    radius = data.particles['Radius']
                if radius <= 0 and data.particles.particle_types is not None:
                    particle_type = data.particles.particle_types
                    radius = data.particles.particle_types.type_by_id(particle_type[i]).radius
                if radius <= 0:
                    radius = data.particles.vis.radius
                    
                # Calculate screen-space size of the particle as a fraction of the canvas height.
                screen_radius = canvas.project_length(positions[i], radius)
                x,y = canvas.project_location(positions[i])
                x += screen_radius*self.px
                y += screen_radius*self.py
              
                canvas.draw_text(
                    f"{prop[i]}",
                    (x, y),
                    font_size=self.font_size,
                    color=self.text_color,
                    outline_width=self.outline_width,
                    outline_color=self.outline_color,
                    anchor="center"
                )