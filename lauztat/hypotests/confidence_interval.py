from .hypotest import HypoTest
from scipy.interpolate import interp1d
import numpy as np


class ConfidenceInterval(HypoTest):
    def __init__(self, poinull, poialt, calculator,
                 qtilde=False):

        super(ConfidenceInterval, self).__init__(poinull, calculator, poialt)

        self._pvalues = None
        self._qtilde = qtilde

    @property
    def qtilde(self):
        """
        Returns True if qtilde statistic is used, else False.
        """
        return self._qtilde

    @qtilde.setter
    def qtilde(self, qtilde):
        """
        Set True if qtilde statistic is used, else False.
        """
        self._qtilde = qtilde

    def pvalues(self):
        """
        Returns p-values scanned for the values of the parameters of interest
        in the null hypothesis.
        """
        if self._pvalues is not None:
            return self._pvalues
        else:
            self._pvalues = self._scannll()
            return self._pvalues

    def _scannll(self):

        poinull = self.poinull
        poialt = self.poialt

        pnull, _ = self.calculator.pvalue(poinull, poialt,
                                          qtilde=self.qtilde,
                                          onesided=False)

        return pnull

    def interval(self, alpha=0.32, printlevel=1):
        """
        Returns the confidence level on the parameter of interest.
        """

        pvalues = self.pvalues()
        poivalues = self.poinull.value
        poialt = self.poialt
        poiname = self.poinull.name

        pois = interp1d(pvalues, poivalues, kind='cubic')
        p_m = pvalues[poivalues < pois(np.max(pvalues))]
        p_p = pvalues[poivalues > pois(np.max(pvalues))]
        poivalues_m = poivalues[poivalues < pois(np.max(pvalues))]
        poivalues_p = poivalues[poivalues > pois(np.max(pvalues))]
        pois_m = interp1d(p_m, poivalues_m, kind='cubic')
        pois_p = interp1d(p_p, poivalues_p, kind='cubic')
        poi_m = float(pois_m(alpha))
        poi_p = float(pois_p(alpha))

        bands = {}
        bands["observed"] = poialt.value
        bands["band_p"] = poi_p
        bands["band_m"] = poi_m

        if printlevel > 0:

            msg = "\nConfidence interval on {0}:\n"
            msg += "\t{band_m} < {0} < {band_p} at {1:.2f}% C.L."
            print(msg.format(poiname, 1 - alpha, **bands))

        return bands

    def plot(self, alpha=0.32, ax=None, show=True, **kwargs):

        import matplotlib.pyplot as plt

        pvalues = self.pvalues()
        poivalues = self.poinull.value
        poiname = self.poinull.name

        if ax is None:
            _, ax = plt.subplots(figsize=(10, 8))

        ax.plot(poivalues, pvalues)
        ax.axhline(alpha, color="r")

        ax.set_ylim(0., 1.05)
        ax.set_xlim(np.min(poivalues), np.max(poivalues))
        ax.set_ylabel("1-CL")
        ax.set_xlabel(poiname)
        # ax.legend(loc="best", fontsize=14)

        if show:
            plt.show()
