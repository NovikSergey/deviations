import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fitter import Fitter


class Stat_plotter:
    
    def draw_plots(self, j_file):
        try:
            df = pd.read_json(j_file)
        except ValueError:
            print("please give the path to json file")
            return
        
        print('read json file')


        def draw_heatmap(df):
            heatmap = sns.heatmap(df.corr())
            heatmap.set(title="Heatmap of correlations")
            plt.savefig('plots/heatmap.png', dpi=300, bbox_inches='tight')
            print('save heatmap plot')

        
        def draw_distribution_by_number_of_corners(df):
            corners_df = df[['name', 'gt_corners']].groupby(by='gt_corners').count()
            corners_plot = corners_df.plot(kind='bar', title='Rows distribution  by number of corners',
                                                   ylabel='number of rows', xlabel='amount of corners')
            corners_plot.get_legend().remove()
            plt.xticks(rotation=0, horizontalalignment="center", fontsize=14)
            plt.yticks(fontsize=14)
            plt.grid()
            plt.savefig('plots/Distribution_by_number_of_corners.png', dpi=300, bbox_inches='tight')
            print('save bar distribution by corners')

        
        def draw_boxplot(df, name="Estimation of outliers without filtering",
                                            path='plots/Estimation_without_filtering.png'):
            limited_df = df[["mean","max","min"]]
            red_circle = dict(markerfacecolor='red', marker='o', markeredgecolor='white')
            fig, axs = plt.subplots(1, len(limited_df.columns), figsize=(20,10))
            for i, ax in enumerate(axs.flat):
                ax.boxplot(limited_df.iloc[:,i], flierprops=red_circle)
                ax.set_title(limited_df.columns[i], fontsize=20, fontweight='bold')
                ax.tick_params(axis='y', labelsize=14)
                if name == "Estimation of outliers without filtering":
                    if limited_df.columns[i] == 'min':
                        ax.semilogy()
            plt.suptitle(name, fontsize=20, fontweight='bold')
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print('save boxplot')
        

        def draw_comparison_stds(df, name='Comparison stds without filtering', path='plots/Comparison_stds_without_filtering.png'):
            std_df = pd.DataFrame({
                "all set": df[["mean", "max", "min"]].std().values.tolist(),
                "floor": df[["floor_mean", "floor_max", "floor_min"]].std().values.tolist(),
                "ceiling": df[["ceiling_mean", "ceiling_max", "ceiling_min"]].std().values.tolist()
            },
            index = ['mean', 'max', 'min'])
            std_df.plot(kind='bar', title=name, ylabel='Standard deviation')
            plt.xticks(rotation=0, horizontalalignment="center", fontsize=14)
            plt.yticks(fontsize=14)
            plt.legend(loc=2, prop={'size': 12})
            plt.grid()
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print('save bar stds')
        

        def filter_data(df):
            filter_df = df
            for column in list(df)[3:]:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                filter_df = filter_df[(filter_df[column] > (Q1-1.5*IQR)) & (filter_df[column] < (Q3+1.5*IQR))]
            self.filter_df = filter_df
            print('filter data')
            return filter_df
        

        def draw_comparison(df, filter_df):
            compare_df = pd.DataFrame({"amount of rows": (df.shape[0], filter_df.shape[0])},
                                        index=('row data', 'filtered data'))
            ax = compare_df.plot(kind='bar', title='Comparison after filtration', ylabel='number of rows')
            plt.xticks(rotation=0, horizontalalignment="center", fontsize=12)
            plt.yticks(fontsize=12)
            ax.bar_label(ax.containers[0], label_type='center', fontsize=14)
            plt.savefig('plots/Comparison.png', dpi=300, bbox_inches='tight')
            print('save bar comparison plot')
        

        def draw_mean_hist(filter_df):
            sns.set_style('white')
            sns.set_context("paper", font_scale = 2)
            mean_hist = sns.displot(data=filter_df, x="mean", kind="hist", bins = 100, aspect = 1.5)
            mean_hist.set(title='Mean deviation', xlabel='deviation in degrees')
            plt.grid()
            plt.show()
            plt.savefig('plots/Mean_histogram.png', dpi=300, bbox_inches='tight')
            print('save mean histogram')


        def draw_suited_distribution(filter_df):
            mean_df = filter_df["mean"].values
            f = Fitter(mean_df, distributions=['invgamma', 'f', 'burr12', 'genhyperbolic'])
            f.fit()
            f.summary()
            plt.title("Suitable distributions")
            plt.savefig('plots/Suited_distribution.png', dpi=300, bbox_inches='tight')
            print('save suited distribution for histogram')


        def draw_floor_ceiling_hist(filter_df):
            plt.figure()
            filter_df[["floor_mean", "ceiling_mean"]].plot(kind='hist',
             title='Comparison floor and ceiling mean', alpha=0.8, bins=50)
            plt.xlabel('deviation in degrees')
            plt.grid()
            plt.savefig('plots/Comparison_floor_ceiling_histogram.png', dpi=300, bbox_inches='tight')
            print('save comparison histogram')


        def draw_comparison_means_in_ranges(filter_df):
            deviation_df = pd.DataFrame({},
            index = ['0-1', '1-2', '2-3', '3-5', '5-10', '10-20','20-30'])
            df_mean_ranges = filter_df

            for m,label in zip(("mean", "floor_mean", "ceiling_mean"),("all set", "floor", "ceiling")):
                df_mean_ranges["ranges"] = pd.cut(df_mean_ranges[m], [0,1,2,3,5,10,20,30])
                df_ranges = df_mean_ranges[[m, "ranges"]].groupby(by="ranges").count()
                df_ranges['percentages'] = (df_ranges[m] / df_ranges[m].sum()) * 100
                deviation_df[label] = df_ranges['percentages'].values.tolist()
            deviation_df.plot(kind='bar',title='Comparison mean deviations',
                             xlabel='ranges in degrees', ylabel='percentages')
            plt.xticks(rotation=0, horizontalalignment="center", fontsize=14)
            plt.yticks(fontsize=14)
            plt.grid()
            plt.savefig('plots/Comparison_means_ranges.png', dpi=300, bbox_inches='tight')
            print('save bar comparison mean plot')
        

        draw_heatmap(df)
        draw_distribution_by_number_of_corners(df)
        draw_boxplot(df)
        draw_comparison_stds(df)
        filter_df = filter_data(df)
        draw_boxplot(filter_df, "Estimation of outliers with filtering",
                     'plots/Estimation_with_filtering.png')
        draw_comparison_stds(filter_df, 'Comparison stds with filtering',
                     'plots/Comparison_stds_with_filtering.png')
        draw_comparison(df, filter_df)
        draw_mean_hist(filter_df)
        draw_suited_distribution(filter_df)
        draw_floor_ceiling_hist(filter_df)
        draw_comparison_means_in_ranges(filter_df)


if __name__ == '__main__':
    analyzator = Stat_plotter()
    analyzator.draw_plots('./deviation.json')
    