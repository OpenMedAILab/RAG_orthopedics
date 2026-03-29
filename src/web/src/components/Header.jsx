import React, { useState, useEffect, useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Menu, MenuItem, ListItemIcon, ListItemText, LinearProgress } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LoginIcon from '@mui/icons-material/Login';
import LogoutIcon from '@mui/icons-material/Logout';
import { StoreContext } from '../contexts/StoreContext';
import { AuthService } from '../services/authService';
import { Events, eventManager } from '../utils/eventManager';
import LoginDialog from './LoginDialog';

const Header = () => {
  const { state, dispatch } = useContext(StoreContext);
  const { currentUser, isAuthenticated } = state;
  const [anchorEl, setAnchorEl] = useState(null);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    try {
      setLoading(true);
      await AuthService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setLoading(false);
      handleMenuClose();
    }
  };

  useEffect(() => {
    // Check authentication status when component mounts
    const checkAuth = async () => {
      if (!isAuthenticated) {
        await AuthService.checkAuth();
      }
    };

    checkAuth();
  }, [isAuthenticated]);

  const handleLoginClick = () => {
    setIsLoginOpen(true);
    handleMenuClose();
  };

  return (
    <>
      <AppBar position="static" sx={{ backgroundColor: 'primary.main', mb: 3 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            医学问答评分系统
          </Typography>
          
          <Box>
            {loading ? (
              <LinearProgress color="secondary" sx={{ width: '100px', alignSelf: 'center' }} />
            ) : isAuthenticated ? (
              <div>
                <Button
                  color="inherit"
                  onClick={handleMenuOpen}
                  startIcon={<AccountCircleIcon />}
                  sx={{ textTransform: 'none' }}
                >
                  {currentUser?.realName || currentUser?.username || '用户'}
                </Button>

                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  <MenuItem onClick={handleLogout}>
                    <ListItemIcon>
                      <LogoutIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>登出</ListItemText>
                  </MenuItem>
                </Menu>
              </div>
            ) : (
              <Button
                color="inherit"
                onClick={() => setIsLoginOpen(true)}
                startIcon={<LoginIcon />}
                sx={{ textTransform: 'none' }}
              >
                登录
              </Button>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      <LoginDialog
        open={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLoginSuccess={(userData) => {
          setCurrentUser(userData);
          setIsAuthenticated(true);
        }}
      />
    </>
  );
};

export default Header;