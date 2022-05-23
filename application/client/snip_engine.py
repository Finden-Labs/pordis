from __future__ import print_function
import os, sys, cairo, random
from PIL import ImageTk, Image
from snippets import get_snippets, Snippet
from datetime import datetime

class SnippetEngine():
    def do_snippet(self, snippet):
        width, height = 256, 256
        surface = cairo.ImageSurface.create_from_png("/home/sba/projects/pordis/application/client/ball.png")
        cr = cairo.Context(surface)

        cr.save()
        snippet.draw_func(cr, width, height)
        cr.restore()
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr.set_source_surface(img, 0, 0)
        cr.paint()
        try:
            os.makedirs(os.path.join("_build", "png"))
        except EnvironmentError:
            pass
        
        random.seed(datetime.now())
        id = str(int(random.randint(1, 9999999999999999))) + snippet.name
        filename = os.path.join("_build", "png", "%s.png" % id)
        surface.write_to_png(filename)
        return id

    if __name__ == '__main__':
        if not(cairo.HAS_IMAGE_SURFACE and cairo.HAS_PNG_FUNCTIONS):
            raise SystemExit(
                'cairo was not compiled with ImageSurface and PNG support')

        #snippets = get_snippets()

        #if len(sys.argv) > 1:
            # do specified snippets
            #selected = [snippets[n] for n in sys.argv[1:]]
        #else:
            # do all snippets
            #selected = snippets.values()

        #for s in selected:
            #do_snippet(s)