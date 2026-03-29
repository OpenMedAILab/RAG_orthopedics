import React from 'react';
import { Paper, Typography, Box, Button, Chip } from '@mui/material';

const Sidebar = ({ items, currentIndex, onSelectItem }) => {
  return (
    <Paper elevation={3} sx={{ p: 2, height: 'fit-content' }}>
      <Typography variant="h6" gutterBottom>
        评分项目
      </Typography>
      
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(60px, 1fr))', 
        gap: 1,
        maxHeight: '400px',
        overflowY: 'auto',
        p: 1
      }}>
        {items.map((item, index) => (
          <Button
            key={item.index}
            variant={index === currentIndex ? "contained" : "outlined"}
            color={
              item.status === 'completed' ? 'success' :
              item.status === 'processing' ? 'warning' : 'primary'
            }
            onClick={() => onSelectItem(index)}
            sx={{
              minWidth: '50px',
              minHeight: '50px',
              fontSize: '0.8rem',
              p: 0.5,
              margin: 0
            }}
          >
            {item.index}
          </Button>
        ))}
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-around', mt: 2, fontSize: '0.75rem' }}>
        <Box display="flex" alignItems="center">
          <Chip label="" size="small" color="primary" sx={{ 
            height: '12px', 
            width: '12px', 
            borderRadius: '50%',
            mr: 1
          }} />
          <span>未评分</span>
        </Box>
        <Box display="flex" alignItems="center">
          <Chip label="" size="small" color="warning" sx={{ 
            height: '12px', 
            width: '12px', 
            borderRadius: '50%',
            mr: 1
          }} />
          <span>进行中</span>
        </Box>
        <Box display="flex" alignItems="center">
          <Chip label="" size="small" color="success" sx={{ 
            height: '12px', 
            width: '12px', 
            borderRadius: '50%',
            mr: 1
          }} />
          <span>已完成</span>
        </Box>
      </Box>
    </Paper>
  );
};

export default Sidebar;