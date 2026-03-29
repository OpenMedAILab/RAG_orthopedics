import React, { useState, useEffect, useContext } from 'react';
import { Container, Box, Grid, Paper, Typography, LinearProgress, Stack, Alert } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';
import CaseInfoCard from './CaseInfoCard';
import CaseContentCard from './CaseContentCard';
import RatingCard from './RatingCard';
import CommentCard from './CommentCard';
import ControlPanel from './ControlPanel';
import { StoreContext } from '../contexts/StoreContext';
import { ApiService } from '../services/apiService';
import { RatingService } from '../services/ratingService';
import { NavigationUtility } from '../utils/navigation';
import { Events, eventManager } from '../utils/eventManager';

const RatingSystem = () => {
  const { state, dispatch } = useContext(StoreContext);
  const {
    allItems,
    currentItem,
    currentIndex,
    loading,
    error,
    currentRatings,
    isAuthenticated,
    currentUser,
    progress
  } = state;

  // Loading items from the API
  useEffect(() => {
    const loadData = async () => {
      try {
        await RatingService.loadAllRatings();
      } catch (err) {
        if (err.message === 'Unauthorized') {
          // Auth error is handled in the service
        }
      }
    };

    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated]);

  const completedCount = allItems.filter(item => item.status === 'completed').length;
  const totalCount = allItems.length;
  const progressPercentage = progress || 0; // Use progress from store

  const handleItemSelect = async (index) => {
    try {
      await RatingService.selectItem(index, allItems, currentUser);
    } catch (error) {
      console.error('Error loading item:', error);
      alert('加载项目时出错: ' + error.message);
    }
  };

  const handleRatingChange = (dimension, value) => {
    RatingService.updateRating(dimension, value);
  };

  const handleCommentChange = (comment) => {
    RatingService.updateComment(comment);
  };

  const handleSaveRatings = async () => {
    await RatingService.saveRatings(currentItem, currentRatings, currentUser);
  };

  const handleNavigation = (direction) => {
    NavigationUtility.handleNavigation(
      direction,
      currentIndex,
      allItems.length,
      (newIndex) => handleItemSelect(newIndex)
    );
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom>
            请先登录以开始评分
          </Typography>
        </Paper>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Box display="flex" flexDirection="column" alignItems="center">
          <LinearProgress sx={{ width: '100%', mb: 2 }} />
          <Typography>加载中...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography color="error" variant="h6" gutterBottom>
            错误: {error}
          </Typography>
          <button onClick={() => window.location.reload()}>重试</button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Header />

      <Stack spacing={2} sx={{ mt: 2 }}>
        <Paper elevation={3} sx={{ p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={6}>
              <Typography variant="subtitle1">
                已完成: {completedCount} / {totalCount}
              </Typography>
            </Grid>
            <Grid item xs={6} textAlign="right">
              <Typography variant="subtitle1">
                完成度: {progressPercentage}%
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <LinearProgress
                variant="determinate"
                value={progressPercentage}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Grid>
          </Grid>
        </Paper>

        <Grid container spacing={3}>
          <Grid item xs={12} md={9}>
            <CaseInfoCard item={currentItem} />
            <CaseContentCard item={currentItem} />
            <RatingCard
              ratings={currentRatings}
              onRatingChange={handleRatingChange}
            />
            <CommentCard
              comment={currentRatings.comment}
              onCommentChange={handleCommentChange}
            />
            <ControlPanel
              currentIndex={currentIndex}
              totalItems={allItems.length}
              onSave={handleSaveRatings}
              onNavigate={handleNavigation}
              hasCompleteRatings={RatingService.hasCompleteRatings(currentRatings)}
            />
          </Grid>

          <Grid item xs={12} md={3}>
            <Sidebar
              items={allItems}
              currentIndex={currentIndex}
              onSelectItem={handleItemSelect}
            />
          </Grid>
        </Grid>
      </Stack>
    </Container>
  );
};

export default RatingSystem;