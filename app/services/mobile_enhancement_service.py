import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

class MobileEnhancementService:
    """Mobile enhancement service for responsive design and mobile-specific features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Mobile breakpoints
        self.breakpoints = {
            'mobile': {'max_width': 768, 'description': 'Mobile devices'},
            'tablet': {'max_width': 1024, 'description': 'Tablet devices'},
            'desktop': {'min_width': 1025, 'description': 'Desktop devices'}
        }
        
        # Mobile-specific features
        self.mobile_features = {
            'touch_gestures': True,
            'swipe_navigation': True,
            'mobile_optimized_charts': True,
            'simplified_ui': True,
            'quick_actions': True,
            'offline_support': False,  # Can be enabled later
            'push_notifications': False  # Can be enabled later
        }
        
        # Responsive design rules
        self.responsive_rules = {
            'mobile': {
                'columns': 1,
                'chart_height': '300px',
                'font_size': '14px',
                'button_size': 'large',
                'spacing': 'compact'
            },
            'tablet': {
                'columns': 2,
                'chart_height': '400px',
                'font_size': '16px',
                'button_size': 'medium',
                'spacing': 'normal'
            },
            'desktop': {
                'columns': 3,
                'chart_height': '500px',
                'font_size': '18px',
                'button_size': 'normal',
                'spacing': 'comfortable'
            }
        }
    
    def get_device_config(self, user_agent: str = None, screen_width: int = None) -> Dict:
        """Detect device type and return configuration"""
        
        try:
            device_type = self._detect_device_type(user_agent, screen_width)
            
            config = {
                'device_type': device_type,
                'breakpoint': self.breakpoints.get(device_type, {}),
                'responsive_rules': self.responsive_rules.get(device_type, {}),
                'mobile_features': self._get_mobile_features(device_type),
                'timestamp': datetime.now().isoformat()
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Device detection failed: {e}")
            return {'device_type': 'desktop', 'error': str(e)}
    
    def _detect_device_type(self, user_agent: str = None, screen_width: int = None) -> str:
        """Detect device type based on user agent and screen width"""
        
        # If screen width is provided, use it
        if screen_width:
            if screen_width <= 768:
                return 'mobile'
            elif screen_width <= 1024:
                return 'tablet'
            else:
                return 'desktop'
        
        # If user agent is provided, analyze it
        if user_agent:
            user_agent_lower = user_agent.lower()
            
            # Mobile indicators
            mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'blackberry', 'windows phone']
            if any(indicator in user_agent_lower for indicator in mobile_indicators):
                if 'ipad' in user_agent_lower:
                    return 'tablet'
                else:
                    return 'mobile'
            
            # Tablet indicators
            tablet_indicators = ['tablet', 'ipad', 'kindle', 'playbook']
            if any(indicator in user_agent_lower for indicator in tablet_indicators):
                return 'tablet'
        
        # Default to desktop
        return 'desktop'
    
    def _get_mobile_features(self, device_type: str) -> Dict:
        """Get mobile-specific features for device type"""
        
        features = self.mobile_features.copy()
        
        if device_type == 'mobile':
            # Enable all mobile features
            features.update({
                'touch_gestures': True,
                'swipe_navigation': True,
                'mobile_optimized_charts': True,
                'simplified_ui': True,
                'quick_actions': True
            })
        elif device_type == 'tablet':
            # Enable most mobile features
            features.update({
                'touch_gestures': True,
                'swipe_navigation': True,
                'mobile_optimized_charts': True,
                'simplified_ui': False,  # Keep full UI for tablets
                'quick_actions': True
            })
        else:  # desktop
            # Disable mobile-specific features
            features.update({
                'touch_gestures': False,
                'swipe_navigation': False,
                'mobile_optimized_charts': False,
                'simplified_ui': False,
                'quick_actions': False
            })
        
        return features
    
    def generate_responsive_css(self, device_type: str) -> str:
        """Generate responsive CSS for the device type"""
        
        try:
            rules = self.responsive_rules.get(device_type, {})
            
            css = f"""
            /* Responsive CSS for {device_type} */
            .device-{device_type} {{
                --columns: {rules.get('columns', 1)};
                --chart-height: {rules.get('chart-height', '400px')};
                --font-size: {rules.get('font-size', '16px')};
                --button-size: {rules.get('button-size', 'medium')};
                --spacing: {rules.get('spacing', 'normal')};
            }}
            
            .device-{device_type} .dashboard-grid {{
                grid-template-columns: repeat(var(--columns), 1fr);
                gap: var(--spacing) === 'compact' ? 10px : var(--spacing) === 'normal' ? 20px : 30px;
            }}
            
            .device-{device_type} .chart-container {{
                height: var(--chart-height);
            }}
            
            .device-{device_type} .trading-signal {{
                font-size: var(--font-size);
                padding: var(--spacing) === 'compact' ? 10px : var(--spacing) === 'normal' ? 15px : 20px;
            }}
            
            .device-{device_type} .btn {{
                padding: var(--button-size) === 'large' ? '12px 24px' : 
                         var(--button-size) === 'medium' ? '10px 20px' : '8px 16px';
                font-size: var(--font-size);
            }}
            """
            
            return css
            
        except Exception as e:
            self.logger.error(f"CSS generation failed: {e}")
            return f"/* Error generating CSS: {e} */"
    
    def generate_mobile_ui_config(self, device_type: str) -> Dict:
        """Generate mobile UI configuration"""
        
        try:
            config = {
                'device_type': device_type,
                'ui_elements': {},
                'navigation': {},
                'charts': {},
                'actions': {}
            }
            
            if device_type == 'mobile':
                config['ui_elements'] = {
                    'header': {'collapsible': True, 'sticky': True},
                    'sidebar': {'collapsible': True, 'overlay': True},
                    'footer': {'collapsible': True, 'sticky': False}
                }
                
                config['navigation'] = {
                    'type': 'bottom_tabs',
                    'swipe_enabled': True,
                    'quick_access': ['signals', 'charts', 'alerts']
                }
                
                config['charts'] = {
                    'type': 'mobile_optimized',
                    'interactions': ['tap', 'pinch_zoom', 'swipe'],
                    'indicators': ['basic'],  # Simplified indicators for mobile
                    'timeframes': ['1m', '5m', '15m', '1h']  # Most important timeframes
                }
                
                config['actions'] = {
                    'quick_actions': ['buy', 'sell', 'hold'],
                    'gesture_actions': {
                        'swipe_left': 'next_timeframe',
                        'swipe_right': 'previous_timeframe',
                        'double_tap': 'toggle_fullscreen'
                    }
                }
                
            elif device_type == 'tablet':
                config['ui_elements'] = {
                    'header': {'collapsible': False, 'sticky': True},
                    'sidebar': {'collapsible': True, 'overlay': False},
                    'footer': {'collapsible': False, 'sticky': False}
                }
                
                config['navigation'] = {
                    'type': 'side_tabs',
                    'swipe_enabled': True,
                    'quick_access': ['signals', 'charts', 'alerts', 'backtesting']
                }
                
                config['charts'] = {
                    'type': 'enhanced',
                    'interactions': ['tap', 'pinch_zoom', 'swipe', 'hover'],
                    'indicators': ['standard'],
                    'timeframes': ['1m', '5m', '15m', '30m', '1h', '4h', '1D']
                }
                
                config['actions'] = {
                    'quick_actions': ['buy', 'sell', 'hold', 'analyze'],
                    'gesture_actions': {
                        'swipe_left': 'next_timeframe',
                        'swipe_right': 'previous_timeframe',
                        'pinch': 'zoom_chart'
                    }
                }
                
            else:  # desktop
                config['ui_elements'] = {
                    'header': {'collapsible': False, 'sticky': False},
                    'sidebar': {'collapsible': False, 'overlay': False},
                    'footer': {'collapsible': False, 'sticky': False}
                }
                
                config['navigation'] = {
                    'type': 'top_menu',
                    'swipe_enabled': False,
                    'quick_access': ['all_features']
                }
                
                config['charts'] = {
                    'type': 'full_featured',
                    'interactions': ['click', 'hover', 'scroll', 'keyboard'],
                    'indicators': ['all'],
                    'timeframes': ['all']
                }
                
                config['actions'] = {
                    'quick_actions': ['all'],
                    'gesture_actions': {}
                }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Mobile UI config generation failed: {e}")
            return {'error': str(e)}
    
    def optimize_charts_for_device(self, chart_config: Dict, device_type: str) -> Dict:
        """Optimize chart configuration for specific device"""
        
        try:
            optimized_config = chart_config.copy()
            
            if device_type == 'mobile':
                # Mobile optimizations
                optimized_config.update({
                    'height': '300px',
                    'width': '100%',
                    'responsive': True,
                    'legend': {'enabled': False},  # Hide legend to save space
                    'tooltip': {'enabled': True, 'shared': False},
                    'navigator': {'enabled': False},  # Disable navigator
                    'rangeSelector': {'enabled': False},  # Disable range selector
                    'scrollbar': {'enabled': False},  # Disable scrollbar
                    'credits': {'enabled': False},  # Hide credits
                    'exporting': {'enabled': False},  # Disable export
                    'plotOptions': {
                        'series': {
                            'animation': False,  # Disable animations for performance
                            'enableMouseTracking': True,
                            'point': {
                                'events': {
                                    'click': True,
                                    'touchstart': True
                                }
                            }
                        }
                    }
                })
                
            elif device_type == 'tablet':
                # Tablet optimizations
                optimized_config.update({
                    'height': '400px',
                    'width': '100%',
                    'responsive': True,
                    'legend': {'enabled': True, 'layout': 'horizontal'},
                    'tooltip': {'enabled': True, 'shared': True},
                    'navigator': {'enabled': True},
                    'rangeSelector': {'enabled': True, 'buttons': ['1h', '1d', '1w']},
                    'scrollbar': {'enabled': True},
                    'credits': {'enabled': False},
                    'exporting': {'enabled': True, 'buttons': {'contextButton': {'enabled': True}}}
                })
                
            else:  # desktop
                # Desktop - keep full features
                optimized_config.update({
                    'height': '500px',
                    'width': '100%',
                    'responsive': True,
                    'legend': {'enabled': True, 'layout': 'horizontal'},
                    'tooltip': {'enabled': True, 'shared': True},
                    'navigator': {'enabled': True},
                    'rangeSelector': {'enabled': True, 'buttons': ['1m', '5m', '15m', '1h', '1d', '1w', '1M']},
                    'scrollbar': {'enabled': True},
                    'credits': {'enabled': True},
                    'exporting': {'enabled': True, 'buttons': {'contextButton': {'enabled': True}}}
                })
            
            return optimized_config
            
        except Exception as e:
            self.logger.error(f"Chart optimization failed: {e}")
            return chart_config
    
    def generate_touch_gestures(self, device_type: str) -> Dict:
        """Generate touch gesture configurations"""
        
        if device_type not in ['mobile', 'tablet']:
            return {}
        
        gestures = {
            'swipe': {
                'left': {'action': 'next_timeframe', 'threshold': 50},
                'right': {'action': 'previous_timeframe', 'threshold': 50},
                'up': {'action': 'zoom_in', 'threshold': 50},
                'down': {'action': 'zoom_out', 'threshold': 50}
            },
            'pinch': {
                'in': {'action': 'zoom_in', 'threshold': 0.8},
                'out': {'action': 'zoom_out', 'threshold': 1.2}
            },
            'double_tap': {
                'action': 'toggle_fullscreen',
                'delay': 300
            },
            'long_press': {
                'action': 'show_context_menu',
                'delay': 500
            }
        }
        
        return gestures
    
    def generate_quick_actions(self, device_type: str) -> List[Dict]:
        """Generate quick action buttons for mobile devices"""
        
        if device_type not in ['mobile', 'tablet']:
            return []
        
        actions = [
            {
                'id': 'quick_buy',
                'label': 'BUY',
                'icon': 'arrow-up',
                'action': 'buy',
                'color': 'success',
                'shortcut': 'swipe_up'
            },
            {
                'id': 'quick_sell',
                'label': 'SELL',
                'icon': 'arrow-down',
                'action': 'sell',
                'color': 'danger',
                'shortcut': 'swipe_down'
            },
            {
                'id': 'quick_hold',
                'label': 'HOLD',
                'icon': 'pause',
                'action': 'hold',
                'color': 'warning',
                'shortcut': 'double_tap'
            },
            {
                'id': 'quick_analyze',
                'label': 'ANALYZE',
                'icon': 'chart-line',
                'action': 'analyze',
                'color': 'info',
                'shortcut': 'long_press'
            }
        ]
        
        # Add device-specific actions
        if device_type == 'tablet':
            actions.extend([
                {
                    'id': 'quick_backtest',
                    'label': 'BACKTEST',
                    'icon': 'calculator',
                    'action': 'backtest',
                    'color': 'primary',
                    'shortcut': 'swipe_left'
                },
                {
                    'id': 'quick_alerts',
                    'label': 'ALERTS',
                    'icon': 'bell',
                    'action': 'alerts',
                    'color': 'secondary',
                    'shortcut': 'swipe_right'
                }
            ])
        
        return actions
    
    def generate_mobile_navigation(self, device_type: str) -> Dict:
        """Generate mobile navigation structure"""
        
        if device_type not in ['mobile', 'tablet']:
            return {}
        
        navigation = {
            'type': 'bottom_tabs' if device_type == 'mobile' else 'side_tabs',
            'tabs': [
                {
                    'id': 'dashboard',
                    'label': 'Dashboard',
                    'icon': 'home',
                    'route': '/',
                    'badge': None
                },
                {
                    'id': 'signals',
                    'label': 'Signals',
                    'icon': 'chart-line',
                    'route': '/signals',
                    'badge': 'count'
                },
                {
                    'id': 'charts',
                    'label': 'Charts',
                    'icon': 'chart-bar',
                    'route': '/charts',
                    'badge': None
                },
                {
                    'id': 'alerts',
                    'label': 'Alerts',
                    'icon': 'bell',
                    'route': '/alerts',
                    'badge': 'count'
                }
            ]
        }
        
        # Add tablet-specific tabs
        if device_type == 'tablet':
            navigation['tabs'].extend([
                {
                    'id': 'backtesting',
                    'label': 'Backtest',
                    'icon': 'calculator',
                    'route': '/backtesting',
                    'badge': None
                },
                {
                    'id': 'volatility',
                    'label': 'Volatility',
                    'icon': 'wave-square',
                    'route': '/volatility',
                    'badge': None
                }
            ])
        
        return navigation
    
    def generate_mobile_css_variables(self, device_type: str) -> Dict:
        """Generate CSS variables for mobile optimization"""
        
        variables = {
            'mobile': {
                '--primary-color': '#007bff',
                '--secondary-color': '#6c757d',
                '--success-color': '#28a745',
                '--danger-color': '#dc3545',
                '--warning-color': '#ffc107',
                '--info-color': '#17a2b8',
                '--light-color': '#f8f9fa',
                '--dark-color': '#343a40',
                '--border-radius': '8px',
                '--box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
                '--transition': 'all 0.3s ease'
            },
            'tablet': {
                '--primary-color': '#007bff',
                '--secondary-color': '#6c757d',
                '--success-color': '#28a745',
                '--danger-color': '#dc3545',
                '--warning-color': '#ffc107',
                '--info-color': '#17a2b8',
                '--light-color': '#f8f9fa',
                '--dark-color': '#343a40',
                '--border-radius': '6px',
                '--box-shadow': '0 1px 3px rgba(0,0,0,0.1)',
                '--transition': 'all 0.2s ease'
            },
            'desktop': {
                '--primary-color': '#007bff',
                '--secondary-color': '#6c757d',
                '--success-color': '#28a745',
                '--danger-color': '#dc3545',
                '--warning-color': '#ffc107',
                '--info-color': '#17a2b8',
                '--light-color': '#f8f9fa',
                '--dark-color': '#343a40',
                '--border-radius': '4px',
                '--box-shadow': '0 1px 2px rgba(0,0,0,0.1)',
                '--transition': 'all 0.15s ease'
            }
        }
        
        return variables.get(device_type, variables['desktop'])
    
    def get_mobile_performance_tips(self, device_type: str) -> List[str]:
        """Get performance optimization tips for mobile devices"""
        
        tips = []
        
        if device_type == 'mobile':
            tips = [
                'Use simplified charts with fewer indicators',
                'Limit real-time updates to essential data',
                'Implement lazy loading for non-critical components',
                'Use CSS transforms instead of position changes',
                'Minimize DOM manipulations',
                'Implement virtual scrolling for long lists',
                'Use requestAnimationFrame for smooth animations',
                'Optimize images and use appropriate formats',
                'Implement service workers for offline support',
                'Use touch events instead of mouse events'
            ]
        elif device_type == 'tablet':
            tips = [
                'Balance between features and performance',
                'Use medium-complexity charts',
                'Implement progressive loading',
                'Optimize for both touch and mouse interactions',
                'Use responsive images with appropriate sizes'
            ]
        
        return tips
    
    def export_mobile_config(self, device_type: str, format: str = 'json') -> str:
        """Export mobile configuration in specified format"""
        
        try:
            config = {
                'device_type': device_type,
                'ui_config': self.generate_mobile_ui_config(device_type),
                'responsive_rules': self.responsive_rules.get(device_type, {}),
                'touch_gestures': self.generate_touch_gestures(device_type),
                'quick_actions': self.generate_quick_actions(device_type),
                'navigation': self.generate_mobile_navigation(device_type),
                'css_variables': self.generate_mobile_css_variables(device_type),
                'performance_tips': self.get_mobile_performance_tips(device_type),
                'timestamp': datetime.now().isoformat()
            }
            
            if format == 'json':
                return json.dumps(config, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Mobile config export failed: {e}")
            return json.dumps({'error': str(e)})
