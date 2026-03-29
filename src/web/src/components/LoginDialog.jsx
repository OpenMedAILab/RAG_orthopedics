import React, { useState, useContext } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Box, Tabs, Tab, Typography, LinearProgress } from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import { AuthService } from '../services/authService';
import { StoreContext } from '../contexts/StoreContext';

const LoginDialog = ({ open, onClose, onLoginSuccess }) => {
  const { dispatch } = useContext(StoreContext);
  const [tab, setTab] = useState(0); // 0 for login, 1 for register
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({
    username: '',
    realname: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLoginChange = (e) => {
    setLoginForm({ ...loginForm, [e.target.name]: e.target.value });
  };

  const handleRegisterChange = (e) => {
    setRegisterForm({ ...registerForm, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await AuthService.login(loginForm.username, loginForm.password);

      if (result.success) {
        if (onLoginSuccess) onLoginSuccess(result.user);
        onClose();
      } else {
        setError(result.message || '登录失败');
      }
    } catch (err) {
      setError(err.message || '登录时发生错误');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (registerForm.password !== registerForm.confirmPassword) {
      setError('密码确认不匹配');
      setLoading(false);
      return;
    }

    try {
      // In this system, registration is handled differently since it's through the backend
      // We'll just show an error since registration isn't typically enabled
      setError('注册功能暂未开放，请联系管理员添加用户');
    } catch (err) {
      setError(err.message || '注册时发生错误');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle textAlign="center">
        {tab === 0 ? '用户登录' : '用户注册'}
      </DialogTitle>

      <Tabs value={tab} onChange={(e, newValue) => setTab(newValue)} centered>
        <Tab label="登录" />
        <Tab label="注册" />
      </Tabs>

      <DialogContent>
        {loading && <LinearProgress />}
        {error && (
          <Typography color="error" variant="body2" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}
        {tab === 0 ? (
          <Box component="form" onSubmit={handleLogin} sx={{ mt: 2 }}>
            <TextField
              name="username"
              label="用户名"
              fullWidth
              margin="normal"
              value={loginForm.username}
              onChange={handleLoginChange}
              required
              disabled={loading}
            />
            <TextField
              name="password"
              label="密码"
              type="password"
              fullWidth
              margin="normal"
              value={loginForm.password}
              onChange={handleLoginChange}
              required
              disabled={loading}
            />
          </Box>
        ) : (
          <Box component="form" onSubmit={handleRegister} sx={{ mt: 2 }}>
            <TextField
              name="username"
              label="用户名"
              fullWidth
              margin="normal"
              value={registerForm.username}
              onChange={handleRegisterChange}
              required
              disabled={loading}
            />
            <TextField
              name="realname"
              label="真实姓名"
              fullWidth
              margin="normal"
              value={registerForm.realname}
              onChange={handleRegisterChange}
              required
              disabled={loading}
            />
            <TextField
              name="password"
              label="密码"
              type="password"
              fullWidth
              margin="normal"
              value={registerForm.password}
              onChange={handleRegisterChange}
              required
              disabled={loading}
            />
            <TextField
              name="confirmPassword"
              label="确认密码"
              type="password"
              fullWidth
              margin="normal"
              value={registerForm.confirmPassword}
              onChange={handleRegisterChange}
              required
              disabled={loading}
            />
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} disabled={loading}>取消</Button>
        {tab === 0 ? (
          <Button variant="contained" onClick={handleLogin} disabled={loading}>
            登录
          </Button>
        ) : (
          <Button variant="contained" onClick={handleRegister} disabled={loading}>
            注册
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default LoginDialog;