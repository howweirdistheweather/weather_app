import math

def Percentile_race(X,dP):
    P = [dP*i for i in range(int(1.0/dP) + 1)]
    return Percentiles(X, P)


def Percentiles(X, P):
    n = len(X)
    if len(P) > 0:
        if n > 1:
            X = sorted(X)
            P = sorted(P)
            P_x = []
            for p in P:
                p_x = p * (n - 1)
                p_x_f = int(math.floor(p_x))
                p_x_c = int(math.ceil(p_x))
                if p_x_f == p_x_c:
                    P_x.append(X[p_x_f])
                else:
                    p_x_d = p_x - p_x_f
                    x_d = X[p_x_c] - X[p_x_f]
                    P_x.append(float(X[p_x_f]) + x_d * p_x_d)
            return P_x
        elif n == 1:
            x = X[0]
            P_x = []
            for p in P:
                P_x.append(x) #Every percentile is the same - the single value
            return P_x
    return 'none'


def Percentiles_tuple(X, P):
    return tuple(Percentiles(X, P))


def Mean(X):
    n = len(X)
    if n > 0:
        return float(sum(X))/n
    else:
        return 'none'


def MinMax(X):
    if len(X) > 0:
        minimum = X[0]
        maximum = X[0]
        for value in X:
            if value > maximum: maximum = value
            if value < minimum: minimum = value
        return (minimum, maximum)
    else:
        return ('none', 'none')


def standard_deviation(X):
    n = len(X)
    if n > 1:
        Xa = Mean(X)
        Sd = 0.0
        for value in X:
            Xdev = value - Xa
            Sd += Xdev * Xdev
        Sd /= n - 1
        return math.sqrt(Sd)
    else:
        return 'none'


def simple_stats(X, dictionary = False):
    n = len(X)
    ave = Mean(X)
    stdev = standard_deviation(X)
    percentiles = Percentiles(X, [0, 0.02, 0.05, 0.25, 0.5, 0.75, 0.95, 0.98, 1])
    if percentiles != 'none':
        mini = percentiles[0]
        p2 = percentiles[1]
        p5 = percentiles[2]
        p25 = percentiles[3]
        median = percentiles[4]
        p75 = percentiles[5]
        p95 = percentiles[6]
        p98 = percentiles[7]
        maxi = percentiles[8]
    else: (mini, p2, p5, p25, median, p75, p95, p98, maxi) = ('none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none')
    if dictionary:
        return {'min':mini, 'max':maxi, 'n':n, 'ave':ave, 'stdev':stdev, 'median':median, 'p25':p25, 'p75':p75, 'p95':p95, 'p5':p5, 'p2':p2, 'p98':p98}
    else: return (mini, maxi, n, ave, stdev, median, p25, p75, p5, p95, p2, p98)


def value_counts(X):
    counts = {}
    for value in X:
        try:
            counts[value] += 1
        except KeyError:
            counts.update([(value, 1)])
    return counts