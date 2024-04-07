// pages/datasubmit/datasubmit.js
Page({

    /**
     * 页面的初始数据
     */
    data: {},

    register(event) {
        wx.showLoading({
            title: '数据上传中',
            mask: true
        })

        var that = this
        console.log(event.detail.value.phone);
        let password = event.detail.value.phone
        this.setData({
            password
        })
        wx.request({

            url: 'http://127.0.0.1:5000/demo', // 这里要替换你的域名的
            data: {name: "12", password, id: "123"},
            method: 'post',
            headers: {
                'Content-Type': 'application/json'
            },
            success: function (res) {
                //console.log("获取到的用户信息成功: " + res.data);
                // 将获取到的JSON数据存入list数组中
                that.setData({
                    dataList: res.data,
                })
                // 在控制台打印
                console.log(res.data)
            },
            complete(res) {
                wx.hideLoading()
            }
        })
    },
    onLoad(options) {

    },

    /**
     * 生命周期函数--监听页面初次渲染完成
     */
    onReady() {

    },

    /**
     * 生命周期函数--监听页面显示
     */
    onShow() {

    },

    /**
     * 生命周期函数--监听页面隐藏
     */
    onHide() {

    },

    /**
     * 生命周期函数--监听页面卸载
     */
    onUnload() {

    },

    /**
     * 页面相关事件处理函数--监听用户下拉动作
     */
    onPullDownRefresh() {

    },

    /**
     * 页面上拉触底事件的处理函数
     */
    onReachBottom() {

    },

    /**
     * 用户点击右上角分享
     */
    onShareAppMessage() {

    }
})