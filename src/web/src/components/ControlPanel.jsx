import React from 'react';
import { Card, CardContent, CardActions, Button, Box } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { NavigationUtility } from '../utils/navigation';

const ControlPanel = ({
  currentIndex,
  totalItems,
  onSave,
  onNavigate,
  hasCompleteRatings
}) => {
  const canNavigatePrev = NavigationUtility.canNavigatePrev(currentIndex);
  const canNavigateNext = NavigationUtility.canNavigateNext(currentIndex, totalItems);

  return (
    <Card sx={{ boxShadow: 3 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
          <Box display="flex" gap={1}>
            <Button
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              onClick={() => onNavigate('prev')}
              disabled={!canNavigatePrev}
            >
              上一条
            </Button>
            <Button
              variant="outlined"
              endIcon={<ArrowForwardIcon />}
              onClick={() => onNavigate('next')}
              disabled={!canNavigateNext}
            >
              下一条
            </Button>
          </Box>

          <Box flex={1} textAlign="center">
            <span>
              {currentIndex + 1} / {totalItems}
            </span>
          </Box>

          <Button
            variant="contained"
            color="success"
            onClick={onSave}
            disabled={!hasCompleteRatings}
          >
            保存当前评分
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ControlPanel;