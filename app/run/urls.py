from django.urls import path

from . import views

app_name = 'run'
urlpatterns = [
    path('', views.index_view, name='index'),
    # pipelines
    # post
    path('postrna/', views.PostRNASeq.as_view(), name='PRSRun'),
    path('postacs/', views.PostAC.as_view(), name='PACSRun'),
    # nf-core
    path('nfcore/rnaseq/', views.RnaSeqRun.as_view(), name='RnaseqRun'),
    path('nfcore/atacseq/', views.AtacSeqRun.as_view(), name='AtacseqRun'),
    path('nfcore/chipseq/', views.ChipSeqRun.as_view(), name='ChipseqRun'),
    path('nfcore/sarek/', views.SarekRun.as_view(), name='SarekRun'),
    # other
    path('crisprcas/', views.CrisprCasView.as_view(), name='CrisprRun'),
    # tutorials
    # post
    path('tutorial/postrna/', views.PostRNASeqTutorial.as_view(), name='PRSTutorial'),
    path('tutorial/postac/', views.PostACSeqTutorial.as_view(), name='PACSTutorial'),
    # nf-core
    path('tutorial/rnaseq/', views.RNASeqTutorial.as_view(), name='RNASTutorial'),
    path('tutorial/chipseq/', views.ChIPSeqTutorial.as_view(), name='ChIPTutorial'),
    path('tutorial/atacseq/', views.ATACSeqTutorial.as_view(), name='ATACTutorial'),
    path('tutorial/sarek/', views.SarekTutorial.as_view(), name='SarekTutorial'),
    # other
    path('tutorial/crisprcas/', views.CrisprCasTutorial.as_view(), name='CrisprCasTutorial'),
    # other views
    path('download_<run_id>/', views.UniversalDownloadView.as_view(), name='UniversalDownload'),
    path('fail_<run_id>_<result>/', views.get_fail_view, name='runFail'),
    path('id_taken_<run_id>/', views.run_id_taken_view, name='idTaken'),
    path('getdownload/', views.get_download_view, name='getDownload'),
    path('detail/<run_id>/', views.detail_view, name='detail'),
    path('igenome/', views.igenome_view, name='iGenome'),
    path('sheets/', views.spreadsheet_view, name='Spreadsheets'),
    path('inputproblem?=<reason>/', views.input_problem_view, name='inputProblems'),
    # path('references/', views.reference_loader_view, name='ReferenceLoader'),
    path('myruns/', views.RunsExecutedListView.as_view(), name='my-runs'),

]
