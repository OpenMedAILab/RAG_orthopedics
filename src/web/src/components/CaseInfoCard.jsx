import React from 'react';
import { Card, CardContent, CardHeader, Grid, Typography, Chip } from '@mui/material';

const CaseInfoCard = ({ item }) => {
  if (!item) return null;

  return (
    <Card sx={{ mb: 2, boxShadow: 3 }}>
      <CardHeader
        title={`病例信息 (${item.case_id || item.case_number || '-'}) - ${item.evaluated_model || item.model || '-'} (${item.evaluated_mode || item.mode || '-'})`}
        action={
          <Chip 
            label={item.status === 'completed' ? '已完成' : 
                   item.status === 'processing' ? '处理中' : '可用'} 
            color={
              item.status === 'completed' ? 'success' : 
              item.status === 'processing' ? 'warning' : 'primary'
            }
            size="small"
          />
        }
      />
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <Typography variant="body2" color="text.secondary">病例号</Typography>
            <Typography>{item.case_id || item.case_number || '-'}</Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="body2" color="text.secondary">模型</Typography>
            <Typography>{item.evaluated_model || item.model || '-'}</Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="body2" color="text.secondary">模式</Typography>
            <Typography>{item.evaluated_mode || item.mode || '-'}</Typography>
          </Grid>
        </Grid>
        
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} sm={4}>
            <Typography variant="body2" color="text.secondary">情境</Typography>
            <Typography>{item.case_data?.context || item.case_data?.情境 || 'N/A'}</Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="body2" color="text.secondary">体格检查</Typography>
            <Typography>{item.case_data?.exam || item.case_data?.体格检查 || 'N/A'}</Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="body2" color="text.secondary">影像学检查</Typography>
            <Typography>{item.case_data?.imaging || item.case_data?.影像学检查 || 'N/A'}</Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default CaseInfoCard;