from typing import Type
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class Stat_plotter:
    
    def draw_plots(self, j_file):
        try:
            df = pd.read_json(j_file)
        except ValueError:
            print("please give the path to json file")
            return
        
        print('read json file')
        Stat_plotter.df = df


        def draw_heatmap(self):
            heatmap = sns.heatmap(self.df.corr())
            heatmap.set(title="Heatmap of correlations")
            plt.savefig('plots/heatmap.png', dpi=300, bbox_inches='tight')
            print('save heatmap plot')

        
        def draw_boxplot_without_filters(self):
            limited_df = self.df[["mean","max","min"]]
            red_circle = dict(markerfacecolor='red', marker='o', markeredgecolor='white')
            fig, axs = plt.subplots(1, len(limited_df.columns), figsize=(20,10))
            for i, ax in enumerate(axs.flat):
                ax.boxplot(limited_df.iloc[:,i], flierprops=red_circle)
                ax.set_title(limited_df.columns[i], fontsize=20, fontweight='bold')
                ax.tick_params(axis='y', labelsize=14)
                if limited_df.columns[i] == 'min':
                     ax.semilogy()
            plt.suptitle("Estimation of outliers without filtering", fontsize=20, fontweight='bold')
            plt.savefig('plots/Estimation_without_filtering.png', dpi=300, bbox_inches='tight')
            print('save boxplot without filter')
        

        def filter_data(self):
            filter_df = self.df
            for colomn in list(df)[3:]:
                Q1 = filter_df[colomn].quantile(0.25)
                Q3 = filter_df[colomn].quantile(0.75)
                IQR = Q3 - Q1
                filter_df = filter_df[(filter_df[colomn] > (Q1-1.5*IQR)) & (filter_df[colomn] < (Q3+1.5*IQR))]
            self.filter_df = filter_df
            print('filter data')

        
        def draw_boxplot_with_filters(self):
            limited_df = self.filter_df[["mean","max","min"]]
            red_circle = dict(markerfacecolor='red', marker='o', markeredgecolor='white')
            fig, axs = plt.subplots(1, len(limited_df.columns), figsize=(20,10))
            for i, ax in enumerate(axs.flat):
                ax.boxplot(limited_df.iloc[:,i], flierprops=red_circle)
                ax.set_title(limited_df.columns[i], fontsize=20, fontweight='bold')
                ax.tick_params(axis='y', labelsize=14)
            plt.suptitle("Estimation of outliers with filtering", fontsize=20, fontweight='bold')
            plt.savefig('plots/Estimation_with_filtering.png', dpi=300, bbox_inches='tight')
            print('save boxplot with filter')
        

        def draw_comparison(self):
            compare_df = pd.DataFrame({"amount of rows": (self.df.shape[0], self.filter_df.shape[0])}, index=('row data', 'filtered data'))
            ax = compare_df.plot(kind='bar', title='Comparison after filtration', ylabel='number of rows')
            plt.xticks(rotation=0, horizontalalignment="center", fontsize=12)
            plt.yticks(fontsize=12)
            ax.bar_label(ax.containers[0], label_type='center', fontsize=14)
            plt.savefig('plots/Comparison.png', dpi=300, bbox_inches='tight')
            print('save bar comparison plot')
        
        
        
        
        draw_heatmap(self)
        draw_boxplot_without_filters(self)
        filter_data(self)
        draw_boxplot_with_filters(self)
        draw_comparison(self)


if __name__ == '__main__':
    analyzator = Stat_plotter()
    analyzator.draw_plots('./deviation.json')
    