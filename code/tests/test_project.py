"""Regression checks for the cohort, launch-year protocol and scoring contract."""
from pathlib import Path
import sys
import unittest
import warnings
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from kickstarter import (FEATURES, GOAL_BINS, GOAL_LABELS, DURATION_BINS,
                         DURATION_LABELS, load_cleaned, validate_cleaned,
                         make_models, evaluate, score_campaign)

class ProjectChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_cleaned()
        cls.train = cls.data.launch_year.isin([2024,2025])
        cls.model = make_models()['Decision Tree'].fit(cls.data.loc[cls.train,FEATURES],cls.data.loc[cls.train,'success'])
        cls.default = dict(funding_goal_usd=12000,duration_days=30,launch_month=3,main_category='Games',country='US')

    def test_verified_cohort(self):
        self.assertEqual(len(self.data),63075)
        self.assertEqual(self.data.groupby('launch_year').size().to_dict(),{2024:20581,2025:25706,2026:16788})
        self.assertEqual(self.data.success.value_counts().to_dict(),{1:44658,0:18417})

    def test_original_bins_and_comparison(self):
        duration=pd.cut(self.data.duration_days,DURATION_BINS,labels=DURATION_LABELS)
        self.assertEqual(pd.cut(pd.Series([14,14.1,30,30.1,45,45.1]),DURATION_BINS,labels=DURATION_LABELS).astype(str).tolist(),['Up to 14 days','>14–30 days','>14–30 days','>30–45 days','>30–45 days','>45–60 days'])
        goal=pd.cut(pd.Series([10000,24999.99,25000]),GOAL_BINS,labels=GOAL_LABELS,right=False).astype(str).tolist()
        self.assertEqual(goal,['$10,000–<$25,000','$10,000–<$25,000','$25,000–<$50,000'])
        narrow=self.data.funding_goal_usd.ge(10000)&self.data.funding_goal_usd.lt(25000)
        for scope,band,n,rate in [(np.ones(len(self.data),dtype=bool),'Up to 14 days',4733,89.2),(np.ones(len(self.data),dtype=bool),'>30–45 days',12677,72.2),(narrow,'Up to 14 days',152,61.8),(narrow,'>30–45 days',2416,66.0)]:
            rows=self.data.loc[scope&duration.eq(band)]
            self.assertEqual(len(rows),n)
            self.assertEqual(round(100*rows.success.mean(),1),rate)

    def test_training_only_preprocessing_and_exact_inputs(self):
        pre=self.model.named_steps['preprocess']
        self.assertEqual(pre.feature_names_in_.tolist(),FEATURES)
        np.testing.assert_allclose(pre.named_transformers_['numeric'].mean_,self.data.loc[self.train,FEATURES[:2]].mean())
        self.assertEqual(int(pre.named_transformers_['numeric'].n_samples_seen_),46287)
        self.assertFalse(np.allclose(pre.named_transformers_['numeric'].mean_,self.data[FEATURES[:2]].mean()))

    def test_failure_class_metrics_and_axes(self):
        result=evaluate([0,0,0,1,1],[0,0,1,0,1])
        self.assertEqual(result['confusion_matrix'],[[2,1],[1,1]])
        self.assertAlmostEqual(result['failure_precision'],2/3)
        self.assertAlmostEqual(result['failure_recall'],2/3)
        self.assertAlmostEqual(result['failure_f1'],2/3)
        self.assertEqual(evaluate([0,1],[1,1])['failure_precision'],0)

    def test_default_and_modified_reuse_fitted_model(self):
        scaler=self.model.named_steps['preprocess'].named_transformers_['numeric']
        mean=scaler.mean_.copy()
        for row,label in [(self.default,'Reaches funding goal'),({**self.default,'funding_goal_usd':1000000,'duration_days':60},'Misses funding goal')]:
            frame,prediction,notes=score_campaign(self.model,row)
            self.assertEqual(frame.columns.tolist(),FEATURES)
            self.assertEqual(prediction,label)
            self.assertEqual(notes,[])
        np.testing.assert_array_equal(mean,scaler.mean_)

    def test_invalid_inputs(self):
        for field,value in [('funding_goal_usd',0),('funding_goal_usd','12,000'),('funding_goal_usd',True),('funding_goal_usd',complex(1,2)),('duration_days',-1),('duration_days',float('inf')),('launch_month',13),('launch_month',3.5),('launch_month','March'),('launch_month',float('nan')),('country','USA'),('country','us'),('country',''),('main_category',' ')]:
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):score_campaign(self.model,{**self.default,field:value})
        with self.assertRaises(ValueError):score_campaign(self.model,{**self.default,'success':1})

    def test_unseen_category_and_country(self):
        row={**self.default,'main_category':'Unseen demo category','country':'ZZ'}
        frame,_,notes=score_campaign(self.model,row)
        self.assertEqual(len(notes),2)
        encoder=self.model.named_steps['preprocess'].named_transformers_['categorical']
        transformed=encoder.transform(frame[FEATURES[2:]]).toarray()[0]
        # Month is seen, but each unknown category and country block is zero.
        offset=len(encoder.categories_[0])
        self.assertEqual(transformed[:offset].sum(),1)
        self.assertEqual(transformed[offset:].sum(),0)

    def test_corrupted_dataset_fails(self):
        for field,value in [('duration_days',-1),('funding_goal_usd',float('inf')),('launch_month',13),('success',3),('country','USA')]:
            data=self.data.copy();data.loc[0,field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_cleaned(data)
        with self.assertRaises(ValueError):validate_cleaned(pd.concat([self.data,self.data.iloc[:1]],ignore_index=True))

if __name__=='__main__':unittest.main(verbosity=2)
