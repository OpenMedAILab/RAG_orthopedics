import React from 'react';
import { Card, CardContent, CardHeader, TextField } from '@mui/material';

const CommentCard = ({ comment, onCommentChange }) => {
  const handleCommentChange = (e) => {
    onCommentChange(e.target.value);
  };

  return (
    <Card sx={{ mb: 2, boxShadow: 3 }}>
      <CardHeader title="评论/备注" />
      <CardContent>
        <TextField
          multiline
          rows={4}
          fullWidth
          placeholder="请输入您的评论或备注..."
          value={comment}
          onChange={handleCommentChange}
          variant="outlined"
        />
      </CardContent>
    </Card>
  );
};

export default CommentCard;