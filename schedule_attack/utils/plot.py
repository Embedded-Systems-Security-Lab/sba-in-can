import matplotlib.pyplot as plt
import pandas as pd

class Plot(object):
    """docstring for Plot"""
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    @staticmethod
    def setup_plot(width=10, height=7.5, sub_fig=111):
        plt.figure(figsize=(width, height))
        ax = plt.subplot(sub_fig)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        return ax

    @staticmethod
    def plot_graph(x,y,figure_name, title, x_label, y_label, rotate=False):

        ax = setup_plot()
        t = tableau20[0]
        t2 = tuple(ti/2 for ti in t)
        plt.plot(x,
            y, '-o',
            lw=2.0,color=t2)
        if rotate:
            plt.xticks(fontsize=14, rotation='vertical')
        else:
            plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        #plt.scatter(x,y, facecolor=tableau20[4],marker="*",s=100)
        plt.title(title, fontsize=24)
        plt.xlabel(x_label, fontsize=20)
        plt.ylabel(y_label, fontsize=20)
        plt.savefig(figure_name)

    @staticmethod
    def plot_multiple_y_graph(x,y,figure_name, title, x_label, y_label, legends, type="scatter"):

        ax = setup_plot()
        for index,values in enumerate(y):
            t = tableau20[index*4]
            t2 = tuple(ti/2 for ti in t)

            if type == 'scatter':
                plt.plot(x,
                    values,  '-o',
                    lw=2.0, color=t2,label=legends[index])
            elif type == 'bar':
                ax.bar(X + (bar_width*index),values,color=t2,label=legends[index],width = bar_width)
            else:
                print('UnKnown type')
                return
        ax.legend(loc='lower right')

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        plt.title(title, fontsize=24)
        plt.xlabel(x_label, fontsize=20)
        plt.ylabel(y_label, fontsize=20)
        plt.savefig(figure_name)
        plt.show()

    @staticmethod
    def plot_box_fig(data, labels,name,x_label='Distance',y_label='Instance number'):
        # if len(data) != len(labels):
        #     raise ValueError('Both labels and data must have equal length')
        l = len(data)
        ax = setup_plot()

        bp = ax.boxplot(data, patch_artist = True,
                notch ='True', vert = 0)
        for i in range(len(bp['boxes'])):
            t = Plot.tableau20[i%len(Plot.tableau20)]
            tab = [x/255 for x in t]
            bp['boxes'][i].set_facecolor(tab)

        for whisker in bp['whiskers']:
            whisker.set(color ='#8B008B',
                linewidth = 1.5,
                linestyle =":")

        for cap in bp['caps']:
            cap.set(color ='#8B008B',
                    linewidth = 2)

        for median in bp['medians']:
            median.set(color ='red',
                    linewidth = 3)

        ax.set_yticklabels([labels])
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel(x_label, fontsize=20)
        plt.ylabel(y_label, fontsize=20)
        plt.savefig(name)


    @staticmethod
    def plot_bar_graph_dict(mydict,figure_name, x_label, y_label,bar_width = 0.8, index=0):
        ax = setup_plot()
        new_tableau = list(Plot.tableau20[index])
        new_tableau = [x/255 for x in new_tableau]
        x = list(mydict.keys())
        x = [str(val) for val in x ]
        y = list(mydict.values())
        ax.bar(x, y, color=new_tableau, width=bar_width)
        #ax.legend(loc='lower right')
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        #x_ticks = np.arange(0, 30, 5)
        #plt.xticks(x_ticks)
        plt.xlabel(x_label, fontsize=20)
        plt.ylabel(y_label, fontsize=20)
        plt.savefig(figure_name)
        plt.show()
