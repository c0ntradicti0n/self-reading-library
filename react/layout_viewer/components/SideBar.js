import React from 'react';
import { ProSidebar, Menu, MenuItem, SubMenu } from 'react-pro-sidebar';


export default class Nav extends React.Component {
    render() {
        return (
            <ProSidebar>
                <Menu iconShape="square">
                    <MenuItem>Dashboard</MenuItem>
                    <SubMenu title="Components" >
                        <MenuItem>Component 1</MenuItem>
                        <MenuItem>Component 2</MenuItem>
                    </SubMenu>
                </Menu>
            </ProSidebar>
        )
    }
}