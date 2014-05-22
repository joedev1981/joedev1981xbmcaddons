# -*- coding: latin-1 -*-

class CItemTypes(object):
    def __init__(self):
        self.types = []
        self.infos = []
        self.items_list = []

    def __getitem__(self, x):
        return self.items_list[self.types.index(x)]

    def __setitem__(self, x, y):
        if x in self.types:
            self.items_list[self.types.index(x)].extend(y[1])
        else:
            self.types.append(x)
            self.infos.append(y[0])
            self.items_list.append(y[1])

    def __delitem__(self, x):
        del self.items_list[x]
        del self.types[x]
        del self.infos[x]

    def __contains__(self, x):
        return x in self.types

    def __len__(self):
        return len(self.types)
    
    def __str__(self):
        txt = []
        for items in self.items_list:
            for item in items:
                txt.append(u'link_title=%s' % item[u'title'])
                txt.extend([u'='.join([u'link_%s' % k, str(v)]) for k,v in item.iteritems() if k != u'title' if k != u'url'])
                txt.append(u'link_url=%s' % item[u'url'])
        return u'\n'.join(txt)

    def files(self):
        return zip(self.types, self.infos, self.items_list)