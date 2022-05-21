

from sage.modules.free_module import FreeModule_ambient_domain, FreeModule_submodule_domain

class FreeModule_ambient_libsingular(FreeModule_ambient_domain):
    pass

class FreeModule_submodule_libsingular(FreeModule_submodule_domain):
    def graded_free_resolution(self, degrees=None, shifts=None):
        """

        EXAMPLES::


        """
        from sage.homology.resolutions.graded import GradedFreeResolution
        return GradedFreeResolution(self, degrees, shifts)

